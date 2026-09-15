import json
from datetime import datetime, timedelta, timezone

from db import transaction
from utils import parse_questions, validate_question_bank


ACTIVE_ASSESSMENT_STATUSES = ("awaiting_manager", "assigned", "submitted")
ASSESSMENT_EXPIRY_DAYS = 30


def utc_now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def create_assessment_request(employee, skill, requested_level):
    employee = employee.strip()
    if not employee:
        raise ValueError("Employee name is required.")

    with transaction() as conn:
        existing = conn.execute(
            """SELECT id FROM assessments
               WHERE employee=? AND skill=? AND status IN (?, ?, ?)
               LIMIT 1""",
            (employee, skill, *ACTIVE_ASSESSMENT_STATUSES),
        ).fetchone()
        if existing:
            return None

        cursor = conn.execute(
            """INSERT INTO assessments
               (employee, skill, requested_level, status, created_at, updated_at)
               VALUES (?, ?, ?, 'awaiting_manager', ?, ?)""",
            (employee, skill, requested_level, utc_now(), utc_now()),
        )
        assessment_id = cursor.lastrowid
        conn.execute(
            """INSERT INTO audit_log
               (entity_type, entity_id, action, actor, details, created_at)
               VALUES ('assessment', ?, 'requested', ?, ?, ?)""",
            (assessment_id, employee, f"Assessment requested for {skill} at {requested_level}", utc_now()),
        )
        return assessment_id


def save_question_bank(skill, level, questions, actor, model, prompt_version):
    validated = validate_question_bank(questions, expected_count=10)
    content = json.dumps(validated)
    with transaction() as conn:
        cursor = conn.execute(
            """INSERT INTO questions
               (skill, level, content, status, created_by, model, prompt_version, created_at)
               VALUES (?, ?, ?, 'draft', ?, ?, ?, ?)""",
            (skill, level, content, actor.strip() or "system", model, prompt_version, utc_now()),
        )
        bank_id = cursor.lastrowid
        conn.execute(
            """INSERT INTO audit_log
               (entity_type, entity_id, action, actor, details, created_at)
               VALUES ('question_bank', ?, 'generated', ?, ?, ?)""",
            (bank_id, actor.strip() or "system", f"Generated 10 questions for {skill} at {level}", utc_now()),
        )
        return bank_id


def parse_and_validate_question_bank(data, expected_count=10):
    return validate_question_bank(parse_questions(data), expected_count=expected_count)


def assign_questions(assessment_id, manager, questions):
    if len(questions) != 5:
        raise ValueError("Exactly five questions must be selected.")
    selected = validate_question_bank(questions, expected_count=5)
    with transaction() as conn:
        result = conn.execute(
                """UPDATE assessments
                    SET selected_questions=?, status='assigned', expires_at=?, updated_at=?
               WHERE id=? AND status='awaiting_manager'""",
                (json.dumps(selected), (datetime.now(timezone.utc) + timedelta(days=ASSESSMENT_EXPIRY_DAYS)).isoformat(timespec="seconds"), utc_now(), assessment_id),
        )
        if result.rowcount != 1:
            raise ValueError("This assessment is no longer awaiting assignment.")
        conn.execute(
            """INSERT INTO audit_log
               (entity_type, entity_id, action, actor, details, created_at)
               VALUES ('assessment', ?, 'assigned', ?, ?, ?)""",
            (assessment_id, manager.strip() or "manager", "Five questions assigned", utc_now()),
        )


def review_question_bank(bank_id, reviewer, approved, note=""):
    status = "approved" if approved else "rejected"
    with transaction() as conn:
        result = conn.execute(
            """UPDATE questions
               SET status=?, reviewed_by=?, reviewed_at=?, review_note=?
               WHERE id=? AND status='draft'""",
            (status, reviewer.strip() or "reviewer", utc_now(), note.strip(), bank_id),
        )
        if result.rowcount != 1:
            raise ValueError("This question bank is no longer a draft.")
        conn.execute(
            """INSERT INTO audit_log
               (entity_type, entity_id, action, actor, details, created_at)
               VALUES ('question_bank', ?, ?, ?, ?, ?)""",
            (bank_id, status, reviewer.strip() or "reviewer", note.strip() or "Question bank reviewed", utc_now()),
        )


def calculate_score(questions, answers):
    if len(questions) != len(answers):
        raise ValueError("One answer is required for every question.")
    correct = 0
    for index, question in enumerate(questions):
        answer_index = question["answer"]
        if isinstance(answer_index, str):
            answer_index = question["options"].index(answer_index)
        if answers[str(index)] == question["options"][answer_index]:
            correct += 1
    return correct / len(questions) if questions else 0.0


def submit_assessment(assessment_id, employee, questions, answers, evidence):
    evidence = evidence.strip()
    if not evidence:
        raise ValueError("Evidence is required before submission.")
    if len(questions) != 5:
        raise ValueError("An assessment must contain exactly five questions.")
    score = calculate_score(questions, answers)
    with transaction() as conn:
        row = conn.execute(
            "SELECT status, expires_at FROM assessments WHERE id=? AND employee=?",
            (assessment_id, employee.strip()),
        ).fetchone()
        if row is None or row[0] != "assigned":
            raise ValueError("This assessment is no longer available for submission.")
        if row[1] and row[1] < utc_now():
            raise ValueError("This assessment has expired. Request a new assessment.")
        result = conn.execute(
            """UPDATE assessments
               SET score=?, status='submitted', evidence=?, answers=?, submitted_at=?,
                   submission_count=COALESCE(submission_count, 0) + 1, updated_at=?
               WHERE id=? AND employee=? AND status='assigned'""",
            (score, evidence, json.dumps(answers), utc_now(), utc_now(), assessment_id, employee.strip()),
        )
        if result.rowcount != 1:
            raise ValueError("This assessment was already submitted.")
        conn.execute(
            """INSERT INTO audit_log
               (entity_type, entity_id, action, actor, details, created_at)
               VALUES ('assessment', ?, 'submitted', ?, ?, ?)""",
            (assessment_id, employee.strip(), f"Score: {score:.2f}", utc_now()),
        )
    return score


def save_manager_review(assessment_id, manager, decision, level, study_plan, note):
    if decision not in ("confirmed", "sent_back"):
        raise ValueError("Invalid manager decision.")
    with transaction() as conn:
        result = conn.execute(
            """UPDATE assessments
               SET status=?, current_level=?, training_need=?, study_plan=?, manager_note=?, updated_at=?
               WHERE id=? AND status='submitted'""",
            (decision, level, f"Next step after {level}", study_plan, note.strip(), utc_now(), assessment_id),
        )
        if result.rowcount != 1:
            raise ValueError("This assessment is no longer awaiting manager review.")
        conn.execute(
            """INSERT INTO audit_log
               (entity_type, entity_id, action, actor, details, created_at)
               VALUES ('assessment', ?, ?, ?, ?, ?)""",
            (assessment_id, decision, manager.strip() or "manager", study_plan, utc_now()),
        )


def level_for_score(score):
    return "Advanced" if score >= 0.8 else "Intermediate" if score >= 0.6 else "Beginner"

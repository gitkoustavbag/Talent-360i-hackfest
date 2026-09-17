import pandas as pd

from db import load_input_sheet, load_optional_output_sheet


def score_to_level(score_pct):
    """Map a percentage score to a discrete proficiency level used in the workbook."""
    if score_pct is None:
        return 0
    score_pct = float(score_pct)
    if score_pct >= 90:
        return 5
    if score_pct >= 80:
        return 4
    if score_pct >= 70:
        return 3
    if score_pct >= 50:
        return 2
    if score_pct > 0:
        return 1
    return 0


def assessment_outcome(score_pct, critical_fail_flag=False, comment=None):
    """Return a consistent pass/fail and recommended current level for an assessment result."""
    score_pct = float(score_pct or 0)
    critical_fail = bool(critical_fail_flag)
    pass_fail = "Fail" if critical_fail or score_pct < 75 else "Pass"
    level = score_to_level(score_pct)
    if critical_fail and level >= 3:
        level = 2
    elif critical_fail and level < 2:
        level = 1
    return {
        "score_pct": round(score_pct, 2),
        "critical_fail_flag": "Yes" if critical_fail else "No",
        "pass_fail_formula": pass_fail,
        "recommended_current_level": level,
        "ai_result_note": comment or "Application-calculated result awaiting calibration",
    }


def question_ready_for_schedule(question_row):
    """Return True only when a question meets the minimum SME approval and quality gates."""
    if isinstance(question_row, pd.Series):
        row = question_row
    else:
        row = pd.Series(question_row)

    required_text = [
        row.get("question_id"),
        row.get("question_text"),
        row.get("option_a"),
        row.get("option_b"),
        row.get("option_c"),
        row.get("option_d"),
        row.get("correct_option"),
    ]
    if any(pd.isna(value) or str(value).strip() == "" for value in required_text):
        return False

    if str(row.get("sme_review_status", "")).strip() != "Approved":
        return False
    if str(row.get("approved_for_schedule", "")).strip() != "Yes":
        return False
    if str(row.get("critical_flag", "No")).strip().lower() == "yes":
        return False

    confidence = str(row.get("ai_confidence", "")).strip().lower()
    if confidence and confidence not in {"high", "medium", "low"}:
        return False

    return True


def get_approved_questions_for_assignment(question_bank, blueprint_id, role_id, skill_id):
    """Return only questions that are ready for scheduling for a given blueprint/role/skill."""
    if isinstance(question_bank, pd.DataFrame):
        df = question_bank.copy()
    else:
        df = pd.DataFrame(question_bank)

    if df.empty:
        return df

    df = df[(df.get("blueprint_id") == blueprint_id) & (df.get("role_id") == role_id)]
    if skill_id is not None:
        df = df[df.get("skill_id") == skill_id]

    ready_mask = df.apply(question_ready_for_schedule, axis=1)
    return df[ready_mask].reset_index(drop=True)


def effective_question_bank():
    """Return complete questions from input and generated output data."""
    input_questions = load_input_sheet("Assessment_QBank")
    generated_questions = load_optional_output_sheet("Assessment_QBank")
    questions = pd.concat([input_questions, generated_questions], ignore_index=True)
    if "question_id" in questions.columns:
        questions = questions.drop_duplicates("question_id", keep="last")

    required_columns = [
        "question_id", "question_text", "option_a", "option_b", "option_c",
        "option_d", "correct_option",
    ]
    questions = questions.dropna(subset=required_columns).copy()
    questions["correct_option"] = questions["correct_option"].astype(str).str.strip().str.upper()
    questions = questions[questions["correct_option"].isin(["A", "B", "C", "D"])]

    reviews = load_optional_output_sheet("SME_Review_Workflow")
    if reviews.empty or "question_id" not in reviews.columns:
        questions["sme_review_status"] = questions.get("sme_review_status", "Pending SME Review")
        questions["approved_for_schedule"] = questions.get("approved_for_schedule", "No")
        return questions

    reviews = reviews.dropna(subset=["question_id"]).drop_duplicates(
        "question_id", keep="last"
    )
    for _, review in reviews.iterrows():
        matches = questions["question_id"] == review["question_id"]
        if not matches.any():
            continue
        questions.loc[matches, "sme_review_status"] = review["sme_review_status"]
        if pd.notna(review.get("sme_decision")):
            questions.loc[matches, "approved_for_schedule"] = (
                "Yes" if review["sme_decision"] == "Approve" else "No"
            )

    if "sme_review_status" not in questions.columns:
        questions["sme_review_status"] = "Pending SME Review"
    if "approved_for_schedule" not in questions.columns:
        questions["approved_for_schedule"] = "No"

    questions["ready_for_schedule"] = questions.apply(question_ready_for_schedule, axis=1)
    return questions
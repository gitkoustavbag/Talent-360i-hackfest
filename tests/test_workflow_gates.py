import unittest

import pandas as pd

from utils import answer_to_option, normalize_difficulty
from workflow import (
    finalize_manager_review,
    deduplicate_open_requests,
    build_tni_recommendation,
    critical_question_failed,
    evaluate_question_mix,
    get_approved_questions_for_assignment,
    question_needs_sme_review,
    question_ready_for_schedule,
    send_back_for_reassessment,
)


class WorkflowGateTests(unittest.TestCase):
    def test_failed_assessment_can_be_sent_back_for_reassessment(self):
        transition = send_back_for_reassessment("Fail", "Revisit control evidence.")
        self.assertEqual(transition["result_status"], "Sent Back")
        self.assertEqual(transition["assignment_status"], "Not Started")
        self.assertEqual(transition["manager_note"], "Revisit control evidence.")

    def test_passed_assessment_cannot_be_sent_back(self):
        with self.assertRaises(ValueError):
            send_back_for_reassessment("Pass")

    def test_approved_critical_question_can_be_scheduled(self):
        row = {
            "question_id": "Q-CRIT",
            "question_text": "Critical question",
            "option_a": "Correct",
            "option_b": "Wrong",
            "option_c": "Other",
            "option_d": "None",
            "correct_option": "A",
            "sme_review_status": "Approved",
            "approved_for_schedule": "Yes",
            "critical_flag": "Yes",
        }
        self.assertTrue(question_ready_for_schedule(row))
        self.assertTrue(critical_question_failed(row, "Wrong"))
        self.assertFalse(critical_question_failed(row, "Correct"))

    def test_normalize_difficulty_does_not_show_target_level_as_difficulty(self):
        self.assertEqual(normalize_difficulty(4), "Unclassified")

    def test_normalize_difficulty_balances_invalid_generated_values(self):
        self.assertEqual(normalize_difficulty(4, index=0, total=10), "Easy")
        self.assertEqual(normalize_difficulty(4, index=4, total=10), "Medium")
        self.assertEqual(normalize_difficulty(4, index=8, total=10), "Hard")

    def test_question_mix_requires_easy_medium_and_hard(self):
        questions = pd.DataFrame(
            [
                {"difficulty": "Easy"},
                {"difficulty": "Medium"},
                {"difficulty": "Medium"},
                {"difficulty": "Hard"},
                {"difficulty": "Medium"},
            ]
        )
        mix = evaluate_question_mix(questions)
        self.assertEqual(mix["status"], "Complete")

    def test_question_mix_reports_missing_difficulty(self):
        mix = evaluate_question_mix([{"difficulty": "Medium"}] * 5)
        self.assertEqual(mix["status"], "Incomplete")
        self.assertEqual(mix["missing"], {"easy": 1, "hard": 1})

    def test_tni_recommendation_maps_gap_and_training(self):
        training = pd.DataFrame([{"skill_id": "S1", "course_id": "COURSE-1"}])
        tni = build_tni_recommendation(4, 2, training, "S1")
        self.assertEqual(tni["gap"], 2)
        self.assertEqual(tni["severity"], "High")
        self.assertEqual(tni["course_id"], "COURSE-1")

    def test_tni_recommendation_handles_unmapped_skill(self):
        tni = build_tni_recommendation(3, 3, pd.DataFrame(), "S1")
        self.assertEqual(tni["severity"], "No gap")
        self.assertEqual(tni["recommendation"], "No action - at target")

    def test_duplicate_open_requests_keep_only_the_newest(self):
        requests = pd.DataFrame(
            [
                {"request_id": "REQ-1", "user_id": "U1", "role_id": "R1", "skill_id": "S1", "target_level": 4, "status": "Requested"},
                {"request_id": "REQ-2", "user_id": "U1", "role_id": "R1", "skill_id": "S1", "target_level": 4, "status": "Requested"},
            ]
        )
        result = deduplicate_open_requests(requests)
        self.assertEqual(result.loc[result["request_id"] == "REQ-1", "status"].iloc[0], "Duplicate")
        self.assertEqual(result.loc[result["request_id"] == "REQ-2", "status"].iloc[0], "Requested")

    def test_rejected_question_is_not_returned_to_sme_queue(self):
        self.assertFalse(question_needs_sme_review("Rejected"))
        self.assertTrue(question_needs_sme_review("Needs Regeneration"))

    def test_answer_to_option_accepts_letter_label(self):
        self.assertEqual(answer_to_option("C", ["Alpha", "Beta", "Gamma", "Delta"]), "C")

    def test_answer_to_option_accepts_option_text(self):
        self.assertEqual(answer_to_option("Gamma", ["Alpha", "Beta", "Gamma", "Delta"]), "C")

    def test_question_ready_for_schedule_accepts_valid_question(self):
        row = {
            "question_id": "Q-001",
            "blueprint_id": "BP-01",
            "role_id": "R-01",
            "skill_id": "S-01",
            "question_text": "What is the required answer?",
            "option_a": "A",
            "option_b": "B",
            "option_c": "C",
            "option_d": "D",
            "correct_option": "B",
            "sme_review_status": "Approved",
            "approved_for_schedule": "Yes",
            "ai_confidence": "High",
            "critical_flag": "No",
        }
        self.assertTrue(question_ready_for_schedule(row))

    def test_question_ready_for_schedule_treats_blank_confidence_as_optional(self):
        row = {
            "question_id": "Q-004",
            "question_text": "What is the required answer?",
            "option_a": "A",
            "option_b": "B",
            "option_c": "C",
            "option_d": "D",
            "correct_option": "B",
            "sme_review_status": "Approved",
            "approved_for_schedule": "Yes",
            "ai_confidence": float("nan"),
            "critical_flag": "No",
        }
        self.assertTrue(question_ready_for_schedule(row))

    def test_question_ready_for_schedule_blocks_unapproved_question(self):
        row = {
            "question_id": "Q-002",
            "blueprint_id": "BP-01",
            "role_id": "R-01",
            "skill_id": "S-01",
            "question_text": "What is the required answer?",
            "option_a": "A",
            "option_b": "B",
            "option_c": "C",
            "option_d": "D",
            "correct_option": "B",
            "sme_review_status": "Pending SME Review",
            "approved_for_schedule": "No",
            "ai_confidence": "Low",
            "critical_flag": "No",
        }
        self.assertFalse(question_ready_for_schedule(row))

    def test_get_approved_questions_for_assignment_filters_only_ready_questions(self):
        df = pd.DataFrame(
            [
                {
                    "question_id": "Q-001",
                    "blueprint_id": "BP-01",
                    "role_id": "R-01",
                    "skill_id": "S-01",
                    "question_text": "Question 1",
                    "option_a": "A",
                    "option_b": "B",
                    "option_c": "C",
                    "option_d": "D",
                    "correct_option": "A",
                    "sme_review_status": "Approved",
                    "approved_for_schedule": "Yes",
                    "ai_confidence": "High",
                    "critical_flag": "No",
                },
                {
                    "question_id": "Q-002",
                    "blueprint_id": "BP-01",
                    "role_id": "R-01",
                    "skill_id": "S-01",
                    "question_text": "Question 2",
                    "option_a": "A",
                    "option_b": "B",
                    "option_c": "C",
                    "option_d": "D",
                    "correct_option": "C",
                    "sme_review_status": "Approved",
                    "approved_for_schedule": "No",
                    "ai_confidence": "Medium",
                    "critical_flag": "No",
                },
                {
                    "question_id": "Q-003",
                    "blueprint_id": "BP-01",
                    "role_id": "R-01",
                    "skill_id": "S-02",
                    "question_text": "Question 3",
                    "option_a": "A",
                    "option_b": "B",
                    "option_c": "C",
                    "option_d": "D",
                    "correct_option": "D",
                    "sme_review_status": "Approved",
                    "approved_for_schedule": "Yes",
                    "ai_confidence": "High",
                    "critical_flag": "No",
                },
            ]
        )

        approved = get_approved_questions_for_assignment(df, "BP-01", "R-01", "S-01")
        self.assertEqual(list(approved["question_id"]), ["Q-001"])

    def test_score_to_level_rounds_to_capability_band(self):
        from workflow import score_to_level

        self.assertEqual(score_to_level(95), 5)
        self.assertEqual(score_to_level(88), 4)
        self.assertEqual(score_to_level(72), 3)
        self.assertEqual(score_to_level(55), 2)
        self.assertEqual(score_to_level(35), 1)

    def test_critical_fail_flags_override_score(self):
        from workflow import assessment_outcome

        outcome = assessment_outcome(72, True, comment="critical failure")
        self.assertEqual(outcome["pass_fail_formula"], "Fail")
        self.assertEqual(outcome["critical_fail_flag"], "Yes")
        self.assertEqual(outcome["recommended_current_level"], 2)

    def test_manager_review_requires_evidence_and_sme_signoff(self):
        review = finalize_manager_review(72, 4, evidence_validated=True, sme_signoff=False)
        self.assertEqual(review["review_status"], "Needs Evidence or SME Signoff")
        self.assertIsNone(review["final_level"])

    def test_manager_review_limits_calibration_to_one_level(self):
        review = finalize_manager_review(72, 5, evidence_validated=True, sme_signoff=True)
        self.assertEqual(review["review_status"], "Finalized")
        self.assertEqual(review["objective_level"], 3)
        self.assertEqual(review["final_level"], 4)


if __name__ == "__main__":
    unittest.main()

import unittest

import pandas as pd

from utils import answer_to_option
from workflow import (
    finalize_manager_review,
    deduplicate_open_requests,
    get_approved_questions_for_assignment,
    question_needs_sme_review,
    question_ready_for_schedule,
)


class WorkflowGateTests(unittest.TestCase):
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

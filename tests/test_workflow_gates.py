import unittest

import pandas as pd

from workflow import get_approved_questions_for_assignment, question_ready_for_schedule


class WorkflowGateTests(unittest.TestCase):
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


if __name__ == "__main__":
    unittest.main()

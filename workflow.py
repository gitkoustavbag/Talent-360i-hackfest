import pandas as pd

from db import load_input_sheet, load_optional_output_sheet


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
    return questions
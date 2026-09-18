import streamlit as st
from datetime import datetime
from theme import apply_theme, audience_banner

from db import append_output_row, load_input_sheet, load_optional_output_sheet, save_output_sheet
from workflow import assessment_outcome, effective_question_bank

apply_theme("employee")

st.markdown("""
<div class="page-header">
    <h2>4. Employee Assessment</h2>
    <div class="muted small">Answer assigned questions and submit your assessment</div>
</div>
""", unsafe_allow_html=True)
audience_banner("employee", "Show what you know", "Answer the questions assigned to your role and skill journey.", "▣")

users = load_input_sheet("Users_Teams")
assignments = load_optional_output_sheet("Assessment_Assignments")
assignment_questions = load_optional_output_sheet("Assessment_Assignment_Questions")
completed = assignments[assignments["assignment_status"] != "Completed"] if not assignments.empty else assignments

if completed.empty:
    st.info("No assigned assessments found.")
else:
    selected_user = st.selectbox(
        "Employee",
        completed["user_id"].drop_duplicates().tolist(),
        format_func=lambda value: users.loc[
            users["user_id"] == value, "synthetic_name"
        ].iloc[0],
    )
    user_assignments = completed[completed["user_id"] == selected_user]
    selected_assignment = st.selectbox("Select Assessment", user_assignments["assignment_id"].tolist())
    assignment = user_assignments[user_assignments["assignment_id"] == selected_assignment].iloc[0]
    question_ids = assignment_questions[
        assignment_questions["assignment_id"] == selected_assignment
    ]["question_id"].tolist()
    question_bank = effective_question_bank()
    questions = question_bank[question_bank["question_id"].isin(question_ids)]

    if questions.empty:
        st.warning("The assigned question set is not available.")
    else:
        answers = {}
        for _, question in questions.iterrows():
            options = [question["option_a"], question["option_b"], question["option_c"], question["option_d"]]
            answers[question["question_id"]] = st.radio(
                question["question_text"], options, key=f"answer_{question['question_id']}"
            )

        if st.button("Submit Assessment"):
            correct = 0
            critical_failure = False
            for _, question in questions.iterrows():
                option_map = {
                    "A": question["option_a"],
                    "B": question["option_b"],
                    "C": question["option_c"],
                    "D": question["option_d"],
                }
                correct_option = str(question["correct_option"]).strip().upper()
                if correct_option not in option_map:
                    st.error(
                        f"Question {question['question_id']} has an invalid correct option and cannot be scored."
                    )
                    st.stop()
                is_correct = answers[question["question_id"]] == option_map[correct_option]
                correct += int(is_correct)
                critical_failure = critical_failure or (
                    str(question.get("critical_flag", "No")).strip().lower() == "yes"
                    and not is_correct
                )
                append_output_row(
                    "Assessment_Responses",
                    {
                        "assignment_id": selected_assignment,
                        "question_id": question["question_id"],
                        "selected_option": answers[question["question_id"]],
                        "is_correct": is_correct,
                        "submitted_at": datetime.now().isoformat(timespec="seconds"),
                    },
                )
            if questions.empty:
                st.error("This assessment has no scorable questions.")
                st.stop()
            score = round(correct / len(questions) * 100, 2)
            outcome = assessment_outcome(score, critical_failure)
            result_id = f"RST-{datetime.now().strftime('%Y%m%d%H%M%S%f')}"
            append_output_row(
                "Assessment_Results",
                {
                    "result_id": result_id,
                    "data_label": "Application-created record",
                    "assignment_id": selected_assignment,
                    "user_id": selected_user,
                    "role_id": assignment["role_id"],
                    "blueprint_id": assignment["blueprint_id"],
                    "schedule_id": assignment["schedule_id"],
                    "score_pct": score,
                    "pass_threshold_pct": 75,
                    "critical_fail_flag": outcome["critical_fail_flag"],
                    "pass_fail_formula": outcome["pass_fail_formula"],
                    "recommended_current_level": outcome["recommended_current_level"],
                    "result_status": "Scored",
                    "ai_result_note": "Application-calculated result awaiting calibration",
                },
            )
            assignments.loc[
                assignments["assignment_id"] == selected_assignment, "assignment_status"
            ] = "Completed"
            save_output_sheet("Assessment_Assignments", assignments)
            st.success(f"Assessment submitted. Score: {score:.2f}%")

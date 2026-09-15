# pages/3_Reviewer_Approval.py
import streamlit as st
from datetime import datetime
from theme import apply_theme, audience_banner

from db import append_output_row
from workflow import effective_question_bank

apply_theme("governance")

st.markdown("""
<div class="page-header">
    <h2>3. Reviewer Approval</h2>
    <div class="muted small">Select questions to approve before scheduling</div>
</div>
""", unsafe_allow_html=True)
audience_banner("governance", "Protect the quality bar", "Approve only the questions that are ready for employee use.", "✓")

question_bank = effective_question_bank()
pending = question_bank[question_bank["sme_review_status"] != "Approved"]

if pending.empty:
    st.info("No assessment questions awaiting SME review.")
else:
    reviewer_role = st.text_input("Reviewer Role")
    question_ids = pending["question_id"].tolist()
    if st.checkbox("Select all pending questions", key="select_all_pending"):
        for question_id in question_ids:
            st.session_state[f"select_{question_id}"] = True

    for _, question in pending.iterrows():
        st.checkbox(
            f"{question['question_id']} | {question['question_text']}",
            key=f"select_{question['question_id']}",
        )
    selected_ids = {
        question_id
        for question_id in question_ids
        if st.session_state.get(f"select_{question_id}", False)
    }

    if st.button("Approve Selected Questions"):
        if not selected_ids:
            st.warning("Select at least one question first.")
            st.stop()
        for question_id in selected_ids:
            question = pending[pending["question_id"] == question_id].iloc[0]
            append_output_row(
                "SME_Review_Workflow",
                {
                    "review_id": f"REV-{datetime.now().strftime('%Y%m%d%H%M%S%f')}",
                    "data_label": "Application-created record",
                    "question_id": question["question_id"],
                    "blueprint_id": question["blueprint_id"],
                    "role_id": question["role_id"],
                    "skill_id": question["skill_id"],
                    "sme_reviewer_role": reviewer_role,
                    "review_round": 1,
                    "sme_review_status": "Approved",
                    "sme_decision": "Approve",
                    "sme_comments_synthetic": "Approved from reviewer selection",
                    "review_date_synthetic": datetime.now().date().isoformat(),
                    "human_in_loop_gate": "Completed",
                },
            )
        st.success(f"Approved {len(selected_ids)} question(s).")

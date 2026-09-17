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
    <div class="muted small">Review each question against the SME governance rubric before scheduling</div>
</div>
""", unsafe_allow_html=True)
audience_banner("governance", "Protect the quality bar", "Approve only the questions that are ready for employee use.", "✓")

question_bank = effective_question_bank()
pending = question_bank[question_bank["sme_review_status"] != "Approved"]

if pending.empty:
    st.info("No assessment questions awaiting SME review.")
else:
    reviewer_role = st.text_input("Reviewer Role")
    decision_map = {
        "Approve": ("Approved", "Yes", "Approved for schedule"),
        "Reject": ("Rejected", "No", "Rejected: not suitable"),
        "Rewrite": ("Needs Revision", "No", "Rewrite required"),
        "Regenerate": ("Needs Regeneration", "No", "Regenerate question"),
    }

    question_ids = pending["question_id"].tolist()
    if st.checkbox("Select all pending questions", key="select_all_pending"):
        for question_id in question_ids:
            st.session_state[f"select_{question_id}"] = True

    selected_ids = set()
    for _, question in pending.iterrows():
        selected = st.checkbox(
            f"{question['question_id']} | {question['question_text']}",
            key=f"select_{question['question_id']}",
        )
        if selected:
            selected_ids.add(question["question_id"])
        decision = st.selectbox(
            f"Decision for {question['question_id']}",
            list(decision_map.keys()),
            index=0,
            key=f"decision_{question['question_id']}",
        )
        st.session_state[f"decision_{question['question_id']}"] = decision

    if st.button("Apply SME Decisions"):
        if not selected_ids:
            st.warning("Select at least one question first.")
            st.stop()
        decisions_applied = 0
        for question_id in selected_ids:
            question = pending[pending["question_id"] == question_id].iloc[0]
            choice = st.session_state.get(f"decision_{question_id}", "Approve")
            status, approved_for_schedule, comment = decision_map[choice]
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
                    "sme_review_status": status,
                    "sme_decision": choice,
                    "sme_comments_synthetic": comment,
                    "review_date_synthetic": datetime.now().date().isoformat(),
                    "human_in_loop_gate": "Completed",
                    "approved_for_schedule": approved_for_schedule,
                },
            )
            decisions_applied += 1
        st.success(f"Applied SME decisions to {decisions_applied} question(s).")

# pages/3_Reviewer_Approval.py
import streamlit as st
from datetime import datetime
from theme import apply_theme, audience_banner

from db import append_output_row, load_optional_output_sheet, save_output_sheet
from workflow import effective_question_bank, question_needs_sme_review, review_question_text

apply_theme("governance")

st.markdown(
        """
        <style>
        div[data-testid='stTextArea'] textarea {
            background: #fff !important;
            border: 1px solid #d9e3dd !important;
            color: #17202a !important;
            caret-color: #167a5a !important;
        }
        div[data-testid='stTextArea'] textarea::placeholder {
            color: #718096 !important;
        }
        div[data-testid='stTextArea'] textarea:focus {
            border-color: #167a5a !important;
            box-shadow: 0 0 0 1px #167a5a !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
)

st.markdown("""
<div class="page-header">
    <h2>3. Reviewer Approval</h2>
    <div class="muted small">Review each question against the SME governance rubric before scheduling</div>
</div>
""", unsafe_allow_html=True)
audience_banner("governance", "Protect the quality bar", "Approve only the questions that are ready for employee use.", "✓")

question_bank = effective_question_bank()
pending = question_bank[
    question_bank["sme_review_status"].map(question_needs_sme_review)
]

if pending.empty:
    st.info("No assessment questions awaiting SME review.")
else:
    reviewer_role = st.text_input("Reviewer Role")
    st.caption(
        "This queue contains new, rewritten, or regeneration-requested questions. "
        "Rejected questions are terminal and are not shown again."
    )
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
    decisions = {}
    edited_texts = {}
    for _, question in pending.iterrows():
        selected = st.checkbox(
            f"{question['question_id']} | {question['question_text']}",
            key=f"select_{question['question_id']}",
        )
        if selected:
            selected_ids.add(question["question_id"])
        edited_texts[question["question_id"]] = st.text_area(
            f"Question text for {question['question_id']}",
            value=str(question["question_text"]),
            key=f"text_{question['question_id']}",
            height=90,
        )
        decision = st.selectbox(
            f"Decision for {question['question_id']}",
            list(decision_map.keys()),
            index=0,
            key=f"decision_{question['question_id']}",
        )
        decisions[question["question_id"]] = decision

    if st.button("Apply SME Decisions"):
        if not selected_ids:
            st.warning("Select at least one question first.")
            st.stop()
        if not reviewer_role.strip():
            st.error("Enter the reviewer role before applying SME decisions.")
            st.stop()
        decisions_applied = 0
        for question_id in selected_ids:
            question = pending[pending["question_id"] == question_id].iloc[0]
            choice = decisions.get(question_id, "Approve")
            status, approved_for_schedule, comment = decision_map[choice]
            edited_text = review_question_text(
                question["question_text"], edited_texts.get(question_id, "")
            )
            question_bank_output = load_optional_output_sheet("Assessment_QBank")
            question_record = question.to_dict()
            question_record["question_text"] = edited_text
            question_record["data_label"] = "Application-created SME wording override"
            if question_bank_output.empty:
                question_bank_output = question_bank_output.from_records([question_record])
            else:
                matches = question_bank_output["question_id"] == question_id
                if matches.any():
                    last_match = question_bank_output.index[matches][-1]
                    for column, value in question_record.items():
                        question_bank_output.loc[last_match, column] = value
                else:
                    question_bank_output = question_bank_output.from_records(
                        [question_record], columns=question_bank_output.columns
                    )
            save_output_sheet("Assessment_QBank", question_bank_output)
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
            append_output_row(
                "App_Audit_Log",
                {
                    "event_id": f"AUD-{question_id}-{datetime.now().strftime('%f')}",
                    "entity_type": "question_review",
                    "entity_id": question_id,
                    "action": choice.lower(),
                    "actor": reviewer_role.strip(),
                    "details": comment,
                    "created_at": datetime.now().isoformat(timespec="seconds"),
                },
            )
            decisions_applied += 1
        st.success(f"Applied SME decisions to {decisions_applied} question(s).")

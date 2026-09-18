# pages/2_Manager_Assignment.py
import streamlit as st
from db import append_output_row, load_input_sheet, load_optional_output_sheet
from datetime import datetime
from theme import apply_theme, audience_banner
from workflow import (
    deduplicate_open_requests,
    effective_question_bank,
    evaluate_question_mix,
    get_approved_questions_for_assignment,
)

apply_theme("manager")

st.markdown("""
<div class="page-header">
    <h2>2. Manager Assignment</h2>
    <div class="muted small">Assign questions from an approved blueprint</div>
</div>
""", unsafe_allow_html=True)
audience_banner("manager", "Turn a request into a ready assessment", "Select the right blueprint, schedule, and approved questions.", "→")

requests = load_optional_output_sheet("Assessment_Requests")
original_request_statuses = requests["status"].copy() if "status" in requests else None
requests = deduplicate_open_requests(requests)
if (
    original_request_statuses is not None and
    not requests["status"].equals(original_request_statuses)
):
    from db import save_output_sheet
    save_output_sheet("Assessment_Requests", requests)
pending = requests[requests["status"] == "Requested"] if "status" in requests else requests

if pending.empty:
    st.info("No pending employee requests.")
else:
    for _, row in pending.iterrows():
        st.subheader(f"{row['skill']} | {row['user_id']} | Target level {row['target_level']}")

        blueprints = load_input_sheet("Assessment_Blueprints")
        question_bank = effective_question_bank()
        schedules = load_input_sheet("Assessment_Schedules")

        matching_blueprints = blueprints[blueprints["role_id"] == row["role_id"]]
        if matching_blueprints.empty:
            st.warning("No assessment blueprint exists for this role.")
            continue

        blueprint_id = st.selectbox(
            "Blueprint",
            matching_blueprints["blueprint_id"].tolist(),
            key=f"blueprint_{row['request_id']}",
            format_func=lambda value: matching_blueprints.loc[
                matching_blueprints["blueprint_id"] == value, "assessment_name"
            ].iloc[0],
        )
        matching_schedules = schedules[schedules["blueprint_id"] == blueprint_id]
        skill_approved = get_approved_questions_for_assignment(
            question_bank,
            blueprint_id,
            row["role_id"],
            row.get("skill_id"),
        )
        approved = skill_approved

        target_count = 5
        if matching_schedules.empty:
            st.warning("No schedule exists for this blueprint.")
        elif len(approved) < target_count:
            st.warning(
                f"Only {len(approved)} approved questions are available for "
                f"{row['skill']} in this blueprint. Approve at least 5 questions "
                "for this exact role, blueprint, and skill before assignment."
            )
            st.page_link(
                "pages/6_Admin_Question_Bank.py",
                label="Open Admin Question Bank to generate missing questions",
            )
        else:
            ready_schedules = matching_schedules[
                matching_schedules["schedule_status"] == "Ready to Schedule"
            ]
            schedule = (ready_schedules if not ready_schedules.empty else matching_schedules).iloc[0]
            if schedule["schedule_status"] != "Ready to Schedule":
                st.info("The schedule is pending approval; assignment is available for workflow testing.")
            selected_ids = st.multiselect(
                f"Select {target_count} questions",
                approved["question_id"].tolist(),
                max_selections=target_count,
                key=f"questions_{row['request_id']}",
                format_func=lambda value: approved.loc[
                    approved["question_id"] == value
                ].apply(
                    lambda question: (
                        f"[{str(question['difficulty']).strip().title()}] "
                        f"{question['question_text']}"
                    ),
                    axis=1,
                ).iloc[0],
            )
            selected_questions = approved[approved["question_id"].isin(selected_ids)]
            mix = evaluate_question_mix(selected_questions)
            if selected_ids:
                mix_counts = ", ".join(
                    f"{difficulty.title()}: {count}"
                    for difficulty, count in sorted(mix["counts"].items())
                )
                st.caption(f"Selected difficulty mix: {mix_counts or 'No difficulty labels'}")
            if selected_ids and len(selected_ids) == target_count and mix["status"] != "Complete":
                missing = ", ".join(
                    f"{difficulty.title()} ({count})"
                    for difficulty, count in mix["missing"].items()
                )
                st.warning(f"Question mix is incomplete. Add: {missing}.")
            if st.button("Assign Assessment", key=f"assign_{row['request_id']}"):
                if len(selected_ids) != target_count:
                    st.error(f"Select exactly {target_count} questions.")
                elif mix["status"] != "Complete":
                    st.error("Select at least one Easy, one Medium, and one Hard question.")
                else:
                    assignment_id = f"ASG-{datetime.now().strftime('%Y%m%d%H%M%S%f')}"
                    append_output_row(
                        "Assessment_Assignments",
                        {
                            "assignment_id": assignment_id,
                            "data_label": "Application-created record",
                            "user_id": row["user_id"],
                            "role_id": row["role_id"],
                            "blueprint_id": blueprint_id,
                            "schedule_id": schedule["schedule_id"],
                            "assigned_date": datetime.now().date().isoformat(),
                            "due_date": schedule["planned_close_date"],
                            "assignment_status": "Not Started",
                            "notes": "Created from approved question bank",
                        },
                    )
                    for question_id in selected_ids:
                        append_output_row(
                            "Assessment_Assignment_Questions",
                            {
                                "assignment_id": assignment_id,
                                "question_id": question_id,
                            },
                        )
                    requests.loc[
                        requests["request_id"] == row["request_id"], "status"
                    ] = "Assigned"
                    from db import save_output_sheet
                    save_output_sheet("Assessment_Requests", requests)
                    st.success(f"Assessment {assignment_id} assigned successfully.")

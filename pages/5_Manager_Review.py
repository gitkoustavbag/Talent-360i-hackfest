import streamlit as st
from datetime import datetime
from theme import apply_theme, audience_banner

from db import append_output_row, load_input_sheet, load_optional_output_sheet, save_output_sheet
from workflow import (
    build_tni_recommendation,
    effective_question_bank,
    finalize_manager_review,
    send_back_for_reassessment,
)

apply_theme("manager")

st.markdown("""
<div class="page-header">
    <h2>5. Manager Review</h2>
    <div class="muted small">Calibrate scored assessments and confirm skill levels</div>
</div>
""", unsafe_allow_html=True)
audience_banner("manager", "Turn scores into direction", "Calibrate the result and make the next development action clear.", "◈")

results = load_optional_output_sheet("Assessment_Results")
submitted = results[results["result_status"] == "Scored"] if not results.empty else results

if submitted.empty:
    st.info("No scored assessments awaiting calibration.")
else:
    levels = load_input_sheet("Proficiency_Levels")
    assignments = load_optional_output_sheet("Assessment_Assignments")
    assignment_questions = load_optional_output_sheet("Assessment_Assignment_Questions")
    question_bank = effective_question_bank()
    role_skills = load_input_sheet("Role_Skill_Map")
    training_map = load_input_sheet("Training_Skill_Map")

    for _, result in submitted.iterrows():
        matching_assignments = assignments[
            assignments["assignment_id"] == result["assignment_id"]
        ]
        if matching_assignments.empty:
            st.warning(f"Assignment {result['assignment_id']} could not be found; review skipped.")
            continue
        assignment = matching_assignments.iloc[0]
        question_ids = assignment_questions[
            assignment_questions["assignment_id"] == result["assignment_id"]
        ]["question_id"]
        matching_questions = question_bank[question_bank["question_id"].isin(question_ids)]
        if matching_questions.empty:
            st.warning(
                f"No question records were found for assignment {result['assignment_id']}; "
                "review skipped."
            )
            continue
        question = matching_questions.iloc[0]
        mapped_skill = role_skills[
            (role_skills["role_id"] == assignment["role_id"]) &
            (role_skills["skill_id"] == question["skill_id"])
        ]
        if mapped_skill.empty:
            st.warning(
                f"Skill mapping for {question['skill_id']} was not found; "
                f"review for {result['result_id']} skipped."
            )
            continue
        mapped_skill = mapped_skill.iloc[0]
        target_level = int(mapped_skill["target_proficiency_level"])
        st.subheader(f"{result['user_id']} | {mapped_skill['skill']}")
        st.write(f"Score: {result['score_pct']}% | Recommended level: {result['recommended_current_level']}")
        calibrated_level = st.selectbox(
            "Calibrated level",
            levels["level"].tolist(),
            index=min(int(result["recommended_current_level"]), len(levels) - 1),
            format_func=lambda value: levels.loc[
                levels["level"] == value, "level_name"
            ].iloc[0],
            key=f"level_{result['result_id']}",
        )
        evidence_validated = st.checkbox(
            "Evidence validated",
            key=f"evidence_{result['result_id']}",
        )
        sme_signoff = st.checkbox(
            "SME signoff recorded",
            key=f"sme_{result['result_id']}",
        )
        reassessment_note = st.text_area(
            "Reassessment note",
            value="",
            placeholder="Explain what the employee should revisit before resubmitting.",
            key=f"reassessment_note_{result['result_id']}",
        )
        if str(result.get("pass_fail_formula", "")).strip().lower() == "fail":
            prior_attempts = int(
                (
                    (results["assignment_id"] == result["assignment_id"]) &
                    (results["result_status"] == "Sent Back")
                ).sum()
            )
            st.caption(f"Reassessment attempt: {prior_attempts + 1} of 2")
            if st.button("Send Back for Reassessment", key=f"send_back_{result['result_id']}"):
                try:
                    transition = send_back_for_reassessment(
                        result["pass_fail_formula"],
                        reassessment_attempts=prior_attempts,
                        note=reassessment_note,
                    )
                except ValueError as error:
                    st.error(str(error))
                    st.stop()
                result_index = results["result_id"] == result["result_id"]
                results.loc[result_index, "result_status"] = transition["result_status"]
                results.loc[result_index, "manager_note"] = transition["manager_note"]
                results.loc[result_index, "reassessment_attempt"] = transition["reassessment_attempt"]
                save_output_sheet("Assessment_Results", results)
                assignment_index = assignments["assignment_id"] == result["assignment_id"]
                assignments.loc[assignment_index, "assignment_status"] = transition["assignment_status"]
                assignments.loc[assignment_index, "notes"] = transition["manager_note"]
                assignments.loc[assignment_index, "due_date"] = transition["reassessment_due_date"]
                save_output_sheet("Assessment_Assignments", assignments)
                st.success(
                    f"Assessment sent back to {result['user_id']} for reassessment."
                )
        if st.button("Confirm Calibration", key=f"calibrate_{result['result_id']}"):
            review = finalize_manager_review(
                result["score_pct"],
                calibrated_level,
                evidence_validated=evidence_validated,
                sme_signoff=sme_signoff,
                critical_fail_flag=str(result.get("critical_fail_flag", "No")).lower() == "yes",
            )
            if review["review_status"] != "Finalized":
                st.warning("Validate evidence and record SME signoff before finalizing this assessment.")
                st.stop()
            result_index = results["result_id"] == result["result_id"]
            results.loc[result_index, "recommended_current_level"] = review["final_level"]
            results.loc[result_index, "final_level"] = review["final_level"]
            results.loc[result_index, "evidence_validated"] = "Yes"
            results.loc[result_index, "sme_signoff"] = "Yes"
            results.loc[result_index, "result_status"] = "Calibrated"
            save_output_sheet("Assessment_Results", results)
            tni = build_tni_recommendation(
                target_level,
                review["final_level"],
                training_map,
                question["skill_id"],
                role_skill_map=role_skills,
                role_id=assignment["role_id"],
            )
            append_output_row(
                "User_Skill_Assessments",
                {
                    "user_skill_assessment_id": f"USA-{datetime.now().strftime('%Y%m%d%H%M%S%f')}",
                    "data_label": "Application-created record",
                    "user_id": result["user_id"],
                    "role_id": assignment["role_id"],
                    "team_id": "",
                    "skill_id": question["skill_id"],
                    "skill": mapped_skill["skill"],
                    "capability": question["skill"],
                    "target_level": target_level,
                    "assessed_current_level": review["final_level"],
                    "assessment_status": "Assessed",
                    "calibration_status": "Calibrated",
                    "source_result_id": result["result_id"],
                    "ai_confidence": "",
                },
            )
            append_output_row(
                "Skill_Gaps_TNI",
                {
                    "gap_id": f"GAP-{datetime.now().strftime('%Y%m%d%H%M%S%f')}",
                    "data_label": "Application-created record",
                    "user_id": result["user_id"],
                    "role_id": assignment["role_id"],
                    "team_id": "",
                    "skill_id": question["skill_id"],
                    "skill": mapped_skill["skill"],
                    "capability": question["skill"],
                    "target_level": target_level,
                    "current_level": review["final_level"],
                    "gap_level_formula": tni["gap"],
                    "gap_severity": tni["severity"],
                    "recommended_course_id": tni["course_id"],
                    "tni_recommendation": tni["recommendation"],
                    "cross_functional_recommendation": tni["cross_functional_recommendation"],
                },
            )
            st.success(f"Calibration saved for {result['result_id']}.")

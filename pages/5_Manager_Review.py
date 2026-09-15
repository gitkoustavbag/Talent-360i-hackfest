import streamlit as st
from datetime import datetime
from theme import apply_theme, audience_banner

from db import append_output_row, load_input_sheet, load_optional_output_sheet, save_output_sheet

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
    question_bank = load_input_sheet("Assessment_QBank")
    role_skills = load_input_sheet("Role_Skill_Map")
    training_map = load_input_sheet("Training_Skill_Map")

    for _, result in submitted.iterrows():
        assignment = assignments[assignments["assignment_id"] == result["assignment_id"]].iloc[0]
        question_ids = assignment_questions[
            assignment_questions["assignment_id"] == result["assignment_id"]
        ]["question_id"]
        question = question_bank[question_bank["question_id"].isin(question_ids)].iloc[0]
        mapped_skill = role_skills[
            (role_skills["role_id"] == assignment["role_id"]) &
            (role_skills["skill_id"] == question["skill_id"])
        ].iloc[0]
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
        if st.button("Confirm Calibration", key=f"calibrate_{result['result_id']}"):
            result_index = results["result_id"] == result["result_id"]
            results.loc[result_index, "recommended_current_level"] = calibrated_level
            results.loc[result_index, "result_status"] = "Calibrated"
            save_output_sheet("Assessment_Results", results)
            gap = max(target_level - int(calibrated_level), 0)
            severity = "No gap" if gap == 0 else "High" if gap >= 2 else "Moderate"
            mapped_training = training_map[training_map["skill_id"] == question["skill_id"]]
            course_id = mapped_training["course_id"].iloc[0] if not mapped_training.empty else None
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
                    "assessed_current_level": calibrated_level,
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
                    "current_level": calibrated_level,
                    "gap_level_formula": gap,
                    "gap_severity": severity,
                    "recommended_course_id": course_id,
                    "tni_recommendation": "No action - at target" if gap == 0 else "Assign mapped microlearning / scenario lab and reassess",
                    "cross_functional_recommendation": "",
                },
            )
            st.success(f"Calibration saved for {result['result_id']}.")

import pandas as pd
import streamlit as st
from theme import apply_theme, audience_banner

from db import load_input_sheet, load_optional_output_sheet

apply_theme("analytics")

st.markdown("""
<div class="page-header">
    <h2>7. Talent Dashboard</h2>
    <div class="muted small">Assessment outcomes, skill levels, and training needs</div>
</div>
""", unsafe_allow_html=True)
audience_banner("analytics", "See where capability is moving", "Read outcomes, calibrated levels, and the gaps that need action.", "▤")

input_results = load_input_sheet("Assessment_Results")
output_results = load_optional_output_sheet("Assessment_Results")
results = pd.concat([input_results, output_results], ignore_index=True, sort=False)

input_skills = load_input_sheet("User_Skill_Assessments")
output_skills = load_optional_output_sheet("User_Skill_Assessments")
skill_assessments = pd.concat([input_skills, output_skills], ignore_index=True, sort=False)

input_gaps = load_input_sheet("Skill_Gaps_TNI")
output_gaps = load_optional_output_sheet("Skill_Gaps_TNI")
gaps = pd.concat([input_gaps, output_gaps], ignore_index=True, sort=False)

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Assessments", len(results))
with col2:
    st.metric("Scored", int((results["result_status"] == "Scored").sum()))
with col3:
    st.metric("Calibrated", int((results["result_status"] == "Calibrated").sum()))
with col4:
    st.metric("High Skill Gaps", int((gaps["gap_severity"] == "High").sum()))

st.subheader("Assessment Results")
st.dataframe(
    results[
        [
            "result_id",
            "user_id",
            "score_pct",
            "pass_fail_formula",
            "recommended_current_level",
            "result_status",
        ]
    ],
    use_container_width=True,
)

st.subheader("Skill Levels")
level_distribution = (
    skill_assessments.groupby(["skill", "assessed_current_level"])
    .size()
    .reset_index(name="count")
)
st.dataframe(level_distribution, use_container_width=True)

st.subheader("Skill Gaps and TNI")
st.dataframe(
    gaps[
        [
            "user_id",
            "skill",
            "target_level",
            "current_level",
            "gap_severity",
            "recommended_course_id",
            "tni_recommendation",
        ]
    ],
    use_container_width=True,
)

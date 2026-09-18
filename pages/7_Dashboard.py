import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from theme import apply_theme, audience_banner

from ai import summarize_dashboard
from db import load_input_sheet, load_optional_output_sheet

apply_theme("analytics")

st.markdown(
        """
        <style>
        .dashboard-hero {
            align-items: flex-end;
            background: linear-gradient(118deg, #17202a 0%, #26455a 58%, #167a5a 100%);
            border-radius: 10px;
            color: #fff;
            display: flex;
            justify-content: space-between;
            margin: 0 0 1.25rem;
            overflow: hidden;
            padding: 24px 28px;
            position: relative;
        }
        .dashboard-hero:after {
            border: 1px solid rgba(255,255,255,.22);
            border-radius: 50%;
            content: '';
            height: 190px;
            position: absolute;
            right: 60px;
            top: -110px;
            width: 190px;
        }
        .dashboard-hero h3 { color: #fff !important; font-size: 1.6rem; margin: 6px 0; position: relative; z-index: 1; }
        .dashboard-hero p { color: #d5e5e6 !important; margin: 0; max-width: 610px; position: relative; z-index: 1; }
        .dashboard-kicker { color: #b9ef76 !important; font-size: .72rem; font-weight: 700; letter-spacing: .14em; position: relative; z-index: 1; }
        .dashboard-hero-stat { border-left: 1px solid rgba(255,255,255,.25); min-width: 130px; padding-left: 24px; position: relative; z-index: 1; }
        .dashboard-hero-stat strong { display: block; font-family: 'Space Grotesk', sans-serif; font-size: 2.5rem; line-height: 1; }
        .dashboard-hero-stat span { color: #d5e5e6 !important; display: block; font-size: .82rem; margin-top: 7px; }
        .dashboard-action { align-items: center; background: #fff; border: 1px solid #e7ece7; border-left: 4px solid #f47b62; border-radius: 7px; display: flex; justify-content: space-between; margin: 0 0 9px; padding: 12px 14px; }
        .dashboard-action strong { color: #17202a; font-family: 'Space Grotesk', sans-serif; font-size: .88rem; }
        .dashboard-action span { color: #b44d3c; font-size: .82rem; font-weight: 700; }
        div[data-testid='column'] > div[data-testid='stMetric'] { height: 100%; }
        div[data-testid='column'] > div:has(> div[data-testid='stMetric']) { height: 100%; }
        div[data-testid='stMetric'] {
            background: #fff;
            border: 1px solid #dfe7e3;
            border-radius: 9px;
            box-shadow: 0 8px 22px rgba(31,45,38,.06);
            height: 92px;
            padding: 15px 16px;
        }
        div[data-testid='stMetric'] label,
        div[data-testid='stMetric'] [data-testid='stMetricLabel'] { color: #52606d !important; }
        div[data-testid='stMetric'] [data-testid='stMetricValue'] { color: #17202a !important; }
        div[data-testid='stMetric'] [data-testid='stMetricDelta'] { color: #167a5a !important; }
        .stButton > button[kind='primary'],
        [data-testid='stBaseButton-primary'] {
            color: #fff !important;
            font-weight: 700 !important;
        }
        .stButton > button[kind='primary'] *,
        [data-testid='stBaseButton-primary'] * { color: #fff !important; }
        .dashboard-chart {
            background: #fff;
            border: 1px solid #dfe7e3;
            border-radius: 9px;
            box-shadow: 0 8px 22px rgba(31,45,38,.05);
            padding: 10px 12px 2px;
        }
        .ai-brief {
            align-items: center;
            background: linear-gradient(118deg, #f3efff 0%, #fff 72%);
            border: 1px solid #d9cdf7;
            border-left: 4px solid #7351a8;
            border-radius: 10px;
            display: flex;
            gap: 14px;
            margin: 1.5rem 0 .8rem;
            padding: 16px 18px;
        }
        .ai-brief-icon {
            align-items: center;
            background: #7351a8;
            border-radius: 9px;
            color: #fff;
            display: inline-flex;
            flex: 0 0 38px;
            font-size: 1.2rem;
            height: 38px;
            justify-content: center;
            width: 38px;
        }
        .ai-brief-title { color: #24183c !important; font-family: 'Space Grotesk', sans-serif; font-size: 1rem; font-weight: 700; }
        .ai-brief-copy { color: #594c6d !important; font-size: .83rem; margin-top: 3px; }
        .ai-brief-tag { color: #7351a8 !important; font-size: .68rem; font-weight: 700; letter-spacing: .1em; margin-left: auto; text-transform: uppercase; }
        .ai-result {
            background: linear-gradient(135deg, #f4f0ff 0%, #fff8fc 100%);
            border: 1px solid #cdbbe9;
            border-left: 4px solid #7351a8;
            border-radius: 10px;
            box-shadow: 0 8px 22px rgba(74,52,111,.09);
            margin: 1rem 0 1.25rem;
            padding: 20px 22px;
        }
        .ai-result p, .ai-result li { color: #332b40 !important; }
        .ai-result h1, .ai-result h2, .ai-result h3 { color: #24183c !important; }
        @media (max-width: 700px) {
            .dashboard-hero { align-items: flex-start; display: block; }
            .dashboard-hero-stat { border-left: 0; margin-top: 20px; padding-left: 0; }
        }
        </style>
        """,
        unsafe_allow_html=True,
)

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

score_values = pd.to_numeric(results.get("score_pct", pd.Series(dtype=float)), errors="coerce").dropna()
pass_count = int((results.get("pass_fail_formula", pd.Series(dtype=str)) == "Pass").sum())
fail_count = int((results.get("pass_fail_formula", pd.Series(dtype=str)) == "Fail").sum())
high_gap_count = int((gaps.get("gap_severity", pd.Series(dtype=str)) == "High").sum())
calibrated_count = int((results.get("result_status", pd.Series(dtype=str)) == "Calibrated").sum())
average_score = round(float(score_values.mean()), 1) if not score_values.empty else 0
evaluated_count = pass_count + fail_count
pass_rate = round(pass_count / evaluated_count * 100) if evaluated_count else 0

st.markdown(
    f"""
    <div class="dashboard-hero">
      <div>
        <div class="dashboard-kicker">PORTFOLIO PULSE / 07</div>
        <h3>Capability, at a glance.</h3>
        <p>Track assessment momentum, see where capability is below target, and turn the signal into a practical next move.</p>
      </div>
      <div class="dashboard-hero-stat">
        <strong>{pass_rate}%</strong>
        <span>pass rate</span>
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)

col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    st.metric("Assessments", len(results))
with col2:
    st.metric("Average score", f"{average_score}%")
with col3:
    st.metric("Pass rate", f"{pass_rate}%", f"{pass_count} passed")
with col4:
    st.metric("Calibrated", calibrated_count)
with col5:
    st.metric("High gaps", high_gap_count, f"{fail_count} failed")

st.markdown("### Read the signal")
analysis_left, analysis_right = st.columns([1.15, .85], gap="large")
with analysis_left:
    st.markdown("#### Outcome mix")
    if pass_count or fail_count:
        outcome_chart = go.Figure(
            data=[
                go.Pie(
                    labels=["Failed", "Passed"],
                    values=[fail_count, pass_count],
                    hole=0.62,
                    marker={"colors": ["#f47b62", "#167a5a"], "line": {"color": "#ffffff", "width": 3}},
                    textinfo="label+percent",
                    textfont={"color": "#17202a", "size": 14},
                    hovertemplate="%{label}: %{value}<extra></extra>",
                )
            ]
        )
        outcome_chart.update_layout(
            height=260,
            margin={"l": 10, "r": 10, "t": 10, "b": 10},
            paper_bgcolor="#ffffff",
            plot_bgcolor="#ffffff",
            font={"color": "#17202a", "family": "DM Sans"},
            showlegend=False,
        )
        st.markdown("<div class='dashboard-chart'>", unsafe_allow_html=True)
        st.plotly_chart(outcome_chart, use_container_width=True, config={"displayModeBar": False})
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.info("Outcome trends will appear after the first assessment.")

with analysis_right:
    st.markdown("#### Immediate attention")
    if high_gap_count:
        high_gaps = gaps[gaps.get("gap_severity") == "High"]
        if "skill" in high_gaps.columns:
            for skill, count in high_gaps["skill"].value_counts().head(4).items():
                st.markdown(
                    f"<div class='dashboard-action'><strong>{skill}</strong><span>{count} high gap{'s' if count != 1 else ''}</span></div>",
                    unsafe_allow_html=True,
                )
    else:
        st.success("No high-severity skill gaps are currently recorded.")

st.markdown("### Development map")
map_left, map_right = st.columns([1.1, .9], gap="large")
with map_left:
    st.markdown("#### Capability distribution")
    if not skill_assessments.empty and {"skill", "assessed_current_level"}.issubset(skill_assessments.columns):
        level_distribution = (
            skill_assessments.groupby(["skill", "assessed_current_level"])
            .size()
            .reset_index(name="count")
            .pivot(index="skill", columns="assessed_current_level", values="count")
            .fillna(0)
        )
        st.bar_chart(level_distribution, height=280)
    else:
        st.info("Calibrated skill levels will appear here.")

with map_right:
    st.markdown("#### Training signals")
    if not gaps.empty and "recommended_course_id" in gaps.columns:
        course_counts = (
            gaps["recommended_course_id"]
            .dropna()
            .astype(str)
            .replace("", pd.NA)
            .dropna()
            .value_counts()
            .head(6)
        )
        if not course_counts.empty:
            st.dataframe(
                course_counts.rename("Gap count").to_frame(),
                use_container_width=True,
                height=280,
            )
        else:
            st.info("No mapped training actions yet.")
    else:
        st.info("No training mapping data yet.")

st.markdown(
        """
        <div class="ai-brief">
            <div class="ai-brief-icon" aria-hidden="true">✦</div>
            <div>
                <div class="ai-brief-title">AI decision brief</div>
                <div class="ai-brief-copy">A concise readout of portfolio signals and practical next actions.</div>
            </div>
            <div class="ai-brief-tag">Evidence grounded</div>
        </div>
        """,
        unsafe_allow_html=True,
)
st.caption("Uses aggregated scores, outcomes, gaps, and course signals. No raw employee answers are sent.")
if st.button("Generate AI Summary", type="primary"):
    gap_counts = (
        gaps["skill"].value_counts().head(5).to_dict()
        if "skill" in gaps.columns
        else {}
    )
    course_values = (
        gaps["recommended_course_id"].dropna().astype(str).replace("", pd.NA).dropna().unique().tolist()
        if "recommended_course_id" in gaps.columns
        else []
    )
    summary_payload = {
        "assessment_count": len(results),
        "scored_count": int((results.get("result_status", pd.Series(dtype=str)) == "Scored").sum()),
        "calibrated_count": calibrated_count,
        "average_score_pct": average_score,
        "pass_count": pass_count,
        "fail_count": fail_count,
        "critical_fail_count": int((results.get("critical_fail_flag", pd.Series(dtype=str)) == "Yes").sum()),
        "gap_counts_by_skill": gap_counts,
        "high_gap_count": high_gap_count,
        "recommended_courses": course_values[:10],
    }
    try:
        with st.spinner("Analyzing the portfolio..."):
            st.markdown(
                f"<div class='ai-result'>{summarize_dashboard(summary_payload)}</div>",
                unsafe_allow_html=True,
            )
    except Exception as error:
        st.warning(f"AI summary unavailable: {error}")

with st.expander("Open detailed assessment records"):
    st.dataframe(results, use_container_width=True, hide_index=True)

with st.expander("Open detailed gap and TNI records"):
    st.dataframe(gaps, use_container_width=True, hide_index=True)

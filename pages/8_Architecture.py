import streamlit as st

from theme import apply_theme


apply_theme()

st.markdown(
    """
    <div class="page-header">
        <h2>8. Architecture</h2>
        <div class="muted small">A simple view of how Talent 360 moves an assessment from request to development action</div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown("### The journey")
st.markdown("Each step adds one layer of governance before the result reaches the dashboard.")

journey = [
    ("01", "Request", "An employee and a role-mapped skill are selected.", "#d9f4e8", "◎"),
    ("02", "Assign", "A manager chooses a blueprint, schedule, and five questions.", "#dceeff", "→"),
    ("03", "Review", "An SME approves questions before they can be scheduled.", "#fff2bd", "✓"),
    ("04", "Assess", "The employee answers the assigned questions.", "#fff0eb", "▣"),
    ("05", "Calibrate", "The manager reviews the score and calibrates the level.", "#d9f4e8", "◈"),
    ("06", "Act", "Skill gaps and training recommendations are recorded.", "#dceeff", "✦"),
]

for index in range(0, len(journey), 3):
    columns = st.columns(3)
    for column, (number, title, description, color, icon) in zip(columns, journey[index:index + 3]):
        with column:
            st.markdown(
                f"""
                <div class="journey-card" style="background:{color}; border:1px solid rgba(23,32,42,.10); border-radius:8px; min-height:150px; padding:18px; margin-bottom:16px;">
                    <div class="journey-icon" aria-hidden="true">{icon}</div>
                    <div style="color:#52606d; font-family:'Space Grotesk',sans-serif; font-size:.78rem; font-weight:700; letter-spacing:.08em;">{number}</div>
                    <div style="color:#17202a; font-family:'Space Grotesk',sans-serif; font-size:1.15rem; font-weight:700; margin:8px 0 6px;">{title}</div>
                    <div style="color:#52606d; font-size:.92rem; line-height:1.45;">{description}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

st.markdown("### How the pieces connect")
st.markdown("The application keeps reference data separate from the records created during the workflow.")

layers = [
    ("Reference workbook", "Users, roles, skills, levels, blueprints, schedules, question bank, and training map.", "#eef8f2"),
    ("Streamlit workflow", "Request, assignment, SME approval, assessment, manager calibration, and dashboard pages.", "#eef5ff"),
    ("Output workbook", "Requests, assignments, responses, results, reviews, skill assessments, gaps, and audit events.", "#fff7dc"),
]

for index, (title, description, color) in enumerate(layers):
    st.markdown(
        f"""
        <div class="architecture-layer" style="display:flex; align-items:center; gap:18px; background:{color}; border:1px solid rgba(23,32,42,.10); border-radius:8px; padding:16px 20px; margin-bottom:8px;">
            <div style="min-width:190px; color:#17202a; font-family:'Space Grotesk',sans-serif; font-weight:700;">{title}</div>
            <div style="color:#52606d; line-height:1.45;">{description}</div>
        </div>
        {"<div class='architecture-arrow'>&darr;</div>" if index < len(layers) - 1 else ""}
        """,
        unsafe_allow_html=True,
    )

st.markdown("### Governance points")
left, right = st.columns(2)
with left:
    st.markdown(
        """
        <div class="card governance-card">
            <strong>Before assessment</strong><br>
            Questions are generated as drafts, reviewed by an SME, and marked eligible before assignment.
        </div>
        """,
        unsafe_allow_html=True,
    )
with right:
    st.markdown(
        """
        <div class="card governance-card">
            <strong>After assessment</strong><br>
            Scores are checked for pass threshold and critical failures, then calibrated into skill-gap actions.
        </div>
        """,
        unsafe_allow_html=True,
    )

st.info("Use the numbered pages in the left navigation to walk through the live workflow.")

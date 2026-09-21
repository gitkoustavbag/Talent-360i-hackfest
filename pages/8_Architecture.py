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
st.markdown("Each step adds a control, decision, or evidence record before the result reaches development action.")

journey = [
    ("01", "Request", "An employee, role-mapped skill, and target level are selected; duplicate open requests are collapsed.", "#d9f4e8", "◎"),
    ("02", "Generate", "AI creates a role and skill-specific draft bank with Easy, Medium, and Hard coverage.", "#dceeff", "✦"),
    ("03", "Approve", "SME decisions control eligibility; rejected questions are terminal and do not return to the queue.", "#fff2bd", "✓"),
    ("04", "Assign", "A manager selects five schedule-ready questions, including the minimum difficulty mix.", "#dceeff", "→"),
    ("05", "Assess", "The employee answers the assignment; critical-question failures trigger auto-fail.", "#fff0eb", "▣"),
    ("06", "Review", "The manager validates evidence and SME signoff, calibrates within one level, or sends a failure back.", "#d9f4e8", "◈"),
    ("07", "Act", "TNI gaps, mapped courses, adjacent skills, and reassessment actions are recorded.", "#dceeff", "✦"),
    ("08", "Interpret", "The dashboard turns outcomes into portfolio signals and an optional aggregated AI brief.", "#fff2bd", "▤"),
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
    ("Reference workbook", "Users, roles, skills, levels, blueprints, schedules, seeded questions, and training map.", "#eef8f2"),
    ("Governed workflow", "Request deduplication, AI question generation, SME decisions, difficulty mix, assessment, review, and reassessment.", "#eef5ff"),
    ("Output workbook", "Requests, assignments, responses, results, reviews, final levels, skill assessments, gaps, notes, and audit events.", "#fff7dc"),
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
            Questions are generated as drafts, checked for structure and difficulty mix, reviewed by an SME, and marked eligible before assignment. Rejected questions remain terminal.
        </div>
        """,
        unsafe_allow_html=True,
    )
with right:
    st.markdown(
        """
        <div class="card governance-card">
            <strong>After assessment</strong><br>
            Scores are checked for pass threshold and critical failures. Managers need evidence and SME signoff before calibration; failed results can be sent back within the reassessment limit.
        </div>
        """,
        unsafe_allow_html=True,
    )

st.info("Use the numbered pages in the left navigation to walk through the live workflow.")

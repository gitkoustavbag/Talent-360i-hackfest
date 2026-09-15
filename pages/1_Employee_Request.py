# pages/1_Employee_Request.py
import streamlit as st
from db import append_output_row, load_input_sheet
from datetime import datetime
from theme import apply_theme, audience_banner

apply_theme("employee")

st.markdown(
    """
    <div class="page-header">
        <h2>1. Employee Request</h2>
        <div class="muted small">Start a focused, role-mapped skill assessment</div>
    </div>
    <div class="request-hero">
        <div>
            <div class="request-kicker">Assessment intake</div>
            <h3>Set the direction for growth.</h3>
            <p>Choose the person, skill, and level that should shape the next assessment.</p>
        </div>
        <div class="request-badge"><span aria-hidden="true">◎</span> Step 1 of 8</div>
    </div>
    <div class="request-rail" aria-label="Workflow progress">
        <span class="active">Request</span><span>Assign</span><span>Review</span><span>Assess</span><span>Grow</span>
    </div>
    <div style="background:#17202a; border-radius:10px; color:#fff; display:flex; gap:28px; justify-content:space-between; margin:0 0 1.5rem; overflow:hidden; padding:18px 22px; position:relative;">
        <div style="position:relative; z-index:1;">
            <div style="color:#d9f4e8; font-size:.74rem; font-weight:700; letter-spacing:.12em; text-transform:uppercase;">Why start here?</div>
            <div style="font-family:'Space Grotesk',sans-serif; font-size:1.05rem; font-weight:700; margin-top:5px;">A better assessment starts with the right question.</div>
        </div>
        <div style="color:#b8c9c2; font-size:.86rem; line-height:1.4; max-width:320px; position:relative; text-align:right; z-index:1;">Role-mapped choices keep the journey relevant, focused, and ready for manager review.</div>
        <div style="background:#f47b62; border-radius:50%; height:110px; opacity:.9; position:absolute; right:-28px; top:-50px; width:110px;"></div>
    </div>
    """,
    unsafe_allow_html=True,
)
audience_banner("employee", "Make the next step feel relevant", "Your role and skill choices shape a focused assessment.", "◎")

users = load_input_sheet("Users_Teams")
roles = load_input_sheet("Role_Master")
role_skills = load_input_sheet("Role_Skill_Map")
levels = load_input_sheet("Proficiency_Levels")

user_options = users["user_id"].tolist()

form_column, profile_column = st.columns([1.25, .75], gap="large")
with form_column:
    st.markdown(
        """
        <div class="request-panel">
            <h4>Build the request</h4>
            <div class="panel-caption">The employee's role controls which skills are available.</div>
        """,
        unsafe_allow_html=True,
    )
    selected_user = st.selectbox("Employee", user_options)
    user = users[users["user_id"] == selected_user].iloc[0]

    mapped_skills = role_skills[role_skills["role_id"] == user["role_id"]].drop_duplicates("skill_id")
    skill_options = mapped_skills["skill_id"].tolist()
    selected_skill = st.selectbox(
        "Select Skill",
        skill_options,
        format_func=lambda skill_id: mapped_skills.loc[
            mapped_skills["skill_id"] == skill_id, "skill"
        ].iloc[0],
    )
    selected_level = st.selectbox(
        "Target Level",
        levels["level"].tolist(),
        format_func=lambda level: levels.loc[
            levels["level"] == level, "level_name"
        ].iloc[0],
    )
    st.markdown('</div>', unsafe_allow_html=True)

with profile_column:
    st.markdown(
        f"""
        <div class="request-profile">
            <h4>Selected employee</h4>
            <div class="panel-caption">Your request will be linked to this role.</div>
            <div class="profile-label">Person</div>
            <div class="profile-value">{user['synthetic_name']}</div>
            <div class="profile-label">Role</div>
            <div class="profile-value">{user['role_name']}</div>
            <div class="request-next">
                <strong>Next: manager assignment</strong>
                <span>An approved five-question assessment will be prepared.</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

if st.button("Submit Request", type="primary"):
    skill = mapped_skills[mapped_skills["skill_id"] == selected_skill].iloc[0]
    role = roles[roles["role_id"] == user["role_id"]].iloc[0]
    request_id = f"REQ-{datetime.now().strftime('%Y%m%d%H%M%S%f')}"
    append_output_row(
        "Assessment_Requests",
        {
            "request_id": request_id,
            "user_id": selected_user,
            "role_id": user["role_id"],
            "role_name": role["role_name"],
            "skill_id": selected_skill,
            "skill": skill["skill"],
            "target_level": selected_level,
            "status": "Requested",
            "created_at": datetime.now().isoformat(timespec="seconds"),
        },
    )
    append_output_row(
        "App_Audit_Log",
        {
            "event_id": f"AUD-{request_id[4:]}",
            "entity_type": "assessment_request",
            "entity_id": request_id,
            "action": "requested",
            "actor": selected_user,
            "details": f"Skill={skill['skill']}, Level={selected_level}",
            "created_at": datetime.now().isoformat(timespec="seconds"),
        },
    )
    st.success("Assessment request submitted successfully!")

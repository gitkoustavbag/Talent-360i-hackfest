import streamlit as st

from db import load_input_sheet, load_optional_output_sheet
from theme import apply_theme, audience_banner


apply_theme()

st.markdown(
    """
    <div class="page-header">
        <h2>9. Data map</h2>
        <div class="muted small">A practical guide to the tabs behind every Talent 360 workflow step</div>
    </div>
    """,
    unsafe_allow_html=True,
)
audience_banner(
    "neutral",
    "Know where the evidence lives",
    "Reference data feeds the workflow. Completed actions are preserved in the output workbook.",
    "⌘",
)

input_tabs = [
    ("Users_Teams", "Employee identity, team, role, and reporting context."),
    ("Role_Master", "Role names and organizational tower metadata."),
    ("Role_Skill_Map", "Skills available for each role."),
    ("Proficiency_Levels", "Target-level labels used in requests and generation."),
    ("Assessment_Blueprints", "Assessment definitions available to managers."),
    ("Assessment_Schedules", "Planned dates and schedule readiness."),
    ("Assessment_QBank", "Seeded questions used by assignment and generated questions reviewed by SMEs."),
    ("Training_Skill_Map", "Training recommendations for identified gaps."),
]
output_tabs = [
    ("Assessment_Requests", "Employee requests created from page 1."),
    ("SME_Review_Workflow", "Reviewer decisions recorded from page 3."),
    ("Assessment_Assignments", "Manager-created assessment assignments."),
    ("Assessment_Assignment_Questions", "Question IDs attached to each assignment."),
    ("Assessment_Responses", "Employee answers and correctness flags."),
    ("Assessment_Results", "Scores, pass or fail status, critical failures, final levels, reassessment status, and manager notes."),
    ("User_Skill_Assessments", "Manager-calibrated employee skill levels."),
    ("Skill_Gaps_TNI", "Skill gaps and training needs for development action."),
    ("App_Audit_Log", "Trace of important workflow actions."),
]

question_count = len(load_input_sheet("Assessment_QBank"))
generated_count = len(load_optional_output_sheet("Assessment_QBank"))
output_record_count = sum(
    len(load_optional_output_sheet(tab_name)) for tab_name, _ in output_tabs
)

st.markdown(
    """
    <div style="background:linear-gradient(120deg,#17202a 0%,#244b49 62%,#167a5a 100%); border-radius:10px; color:white; margin:0 0 24px; overflow:hidden; padding:26px 30px; position:relative;">
        <div style="color:#b9f2d8; font-size:.72rem; font-weight:700; letter-spacing:.14em; text-transform:uppercase;">TALENT 360 DATA LAYER</div>
        <div style="font-family:'Space Grotesk',sans-serif; font-size:1.8rem; font-weight:700; margin:8px 0 6px;">Two workbooks. One traceable journey.</div>
        <div style="color:#e5f4ed; font-size:.96rem; line-height:1.5; max-width:700px;">The input workbook defines the world the assessment operates in. The output workbook records what people decide, answer, score, and do next.</div>
    </div>
    """,
    unsafe_allow_html=True,
)

metrics = st.columns(4)
with metrics[0]:
    st.metric("Reference tabs", len(input_tabs))
with metrics[1]:
    st.metric("Output tabs", len(output_tabs))
with metrics[2]:
    st.metric("Seeded questions", question_count)
with metrics[3]:
    st.metric("Created records", output_record_count + generated_count)

st.markdown("### Workbook roles")
workbook_columns = st.columns(2)
with workbook_columns[0]:
    st.markdown(
        """
        <div style="background:#eef8f2; border:1px solid #cce9d9; border-top:5px solid #167a5a; border-radius:9px; min-height:150px; padding:20px 22px;">
            <div style="color:#167a5a; font-size:.72rem; font-weight:700; letter-spacing:.14em;">READ ONLY</div>
            <div style="color:#17202a; font-family:'Space Grotesk',sans-serif; font-size:1.3rem; font-weight:700; margin:7px 0 3px;">Input workbook</div>
            <div style="color:#52606d; font-family:'Space Grotesk',sans-serif; font-size:.88rem;">Talent360i_Input_Dataset.xlsx</div>
            <div style="border-top:1px solid #cce9d9; margin:15px 0 11px;"></div>
            <div style="color:#52606d; line-height:1.45;">Definitions and starting data that pages use to make their choices.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
with workbook_columns[1]:
    st.markdown(
        f"""
        <div style="background:#fff7dc; border:1px solid #f0dfaa; border-top:5px solid #b47b16; border-radius:9px; min-height:150px; padding:20px 22px;">
            <div style="color:#9a6810; font-size:.72rem; font-weight:700; letter-spacing:.14em;">WRITABLE</div>
            <div style="color:#17202a; font-family:'Space Grotesk',sans-serif; font-size:1.3rem; font-weight:700; margin:7px 0 3px;">Output workbook</div>
            <div style="color:#52606d; font-family:'Space Grotesk',sans-serif; font-size:.88rem;">Talent360i_Output.xlsx</div>
            <div style="border-top:1px solid #f0dfaa; margin:15px 0 11px;"></div>
            <div style="color:#52606d; line-height:1.45;">Workflow evidence created by the application: {output_record_count + generated_count} records currently available.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown("### Tab directory")

def render_tab_list(title, tabs, accent, background):
    st.markdown(
        f"<div style='background:{background}; border-radius:8px 8px 0 0; border-bottom:3px solid {accent}; color:#17202a; font-family:Space Grotesk,sans-serif; font-size:1.1rem; font-weight:700; padding:13px 16px;'>{title}</div>",
        unsafe_allow_html=True,
    )
    for tab_name, description in tabs:
        st.markdown(
            f"""
            <div style="align-items:start; border-bottom:1px solid #e7ece7; display:grid; gap:14px; grid-template-columns:minmax(145px,38%) 1fr; padding:12px 8px;">
                <div style="color:{accent}; font-family:'Space Grotesk',sans-serif; font-size:.82rem; font-weight:700; line-height:1.35; overflow-wrap:anywhere;">{tab_name}</div>
                <div style="color:#52606d; font-size:.86rem; line-height:1.4;">{description}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

list_columns = st.columns(2)
with list_columns[0]:
    render_tab_list("Input tabs the app reads", input_tabs, "#167a5a", "#d9f4e8")
with list_columns[1]:
    render_tab_list("Output tabs the app saves", output_tabs, "#2867a8", "#dceeff")

st.markdown("### Workflow hand-offs")
flow = [
    ("01", "Request", "Users_Teams + Role_Skill_Map + Proficiency_Levels", "Assessment_Requests; duplicate requests marked", "#d9f4e8", "◎"),
    ("02", "Generate", "Role_Master + Assessment_Blueprints + Role_Skill_Map + pending request", "Assessment_QBank with difficulty labels", "#dceeff", "✦"),
    ("03", "Review", "Assessment_QBank", "SME_Review_Workflow; terminal rejected state", "#fff2bd", "✓"),
    ("04", "Assign", "Assessment_Blueprints + Assessment_Schedules + ready Assessment_QBank", "Assessment_Assignments + Assessment_Assignment_Questions", "#dceeff", "→"),
    ("05", "Assess", "Assignment tabs + approved Assessment_QBank", "Assessment_Responses + Assessment_Results", "#fff0eb", "▣"),
    ("06", "Review", "Assessment_Results + Training_Skill_Map + Role_Skill_Map", "Final level, manager evidence/signoff, reassessment status, User_Skill_Assessments + Skill_Gaps_TNI", "#d9f4e8", "◈"),
    ("07", "Interpret", "Assessment_Results + User_Skill_Assessments + Skill_Gaps_TNI", "Dashboard metrics and optional aggregated AI summary", "#fff2bd", "▤"),
]
for number, title, reads, writes, color, icon in flow:
    st.markdown(
        f"""
        <div style="align-items:center; background:#fff; border:1px solid #e7ece7; border-left:5px solid {color}; border-radius:8px; display:grid; gap:14px; grid-template-columns:34px 48px minmax(110px,.55fr) minmax(220px,1fr) minmax(220px,1fr); margin-bottom:9px; padding:12px 15px;">
            <div style="align-items:center; background:{color}; border-radius:6px; display:flex; font-size:1rem; height:30px; justify-content:center; width:30px;">{icon}</div>
            <div style="color:#718096; font-family:'Space Grotesk',sans-serif; font-size:.76rem; font-weight:700; letter-spacing:.08em;">{number}</div>
            <div style="color:#17202a; font-family:'Space Grotesk',sans-serif; font-weight:700;">{title}</div>
            <div style="color:#52606d; font-size:.83rem; line-height:1.4;"><strong style="color:#718096; font-size:.67rem; letter-spacing:.1em;">READS</strong><br>{reads}</div>
            <div style="color:#52606d; font-size:.83rem; line-height:1.4;"><strong style="color:#718096; font-size:.67rem; letter-spacing:.1em;">WRITES</strong><br>{writes}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.info("Input tabs provide the reference layer. Output tabs preserve the decisions and evidence created during the assessment journey.")

# app.py
import streamlit as st
from theme import apply_theme

# Use a wide layout for modern dashboards
st.set_page_config(page_title="Talent 360", layout="wide", page_icon="🎯")

# Talent 360 visual system — injected globally across Streamlit pages.
_TALENT_CSS = r"""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Space+Grotesk:wght@500;600;700&display=swap');
:root{
  --ink:#17202a;
  --ink-soft:#52606d;
  --muted:#718096;
  --paper:#fbfcf8;
  --surface:#ffffff;
  --line:#e7ece7;
  --mint:#d9f4e8;
  --mint-strong:#167a5a;
  --coral:#f47b62;
  --coral-soft:#fff0eb;
  --blue:#dceeff;
  --blue-strong:#2867a8;
  --yellow:#fff2bd;
}
html, body, #root, .stApp{background:var(--paper) !important}
.stApp{color:var(--ink); font-family:'DM Sans', sans-serif}
.stApp h1, .stApp h2, .stApp h3, .stApp h4{font-family:'Space Grotesk', sans-serif; color:var(--ink); letter-spacing:0}
.stApp h1{font-size:2.6rem; line-height:1.05}
.stApp h2{font-size:1.55rem}
.stApp h3{font-size:1.1rem; margin-top:1.4rem}
.block-container{max-width:1180px; padding:2.25rem 3rem 4rem}
.page-header{border-bottom:1px solid var(--line); padding:0 0 1.2rem; margin-bottom:1.5rem; position:relative}
.page-header:before{content:''; display:block; width:42px; height:5px; border-radius:3px; background:var(--coral); margin-bottom:14px}
.page-header h2{margin:0; color:var(--ink)}
.page-header .muted{color:var(--ink-soft); margin-top:5px}
.card{background:var(--surface); border:1px solid var(--line); border-radius:8px; padding:18px; box-shadow:0 10px 30px rgba(31,45,38,.05)}
.kpi{background:var(--surface); border:1px solid var(--line); border-top:4px solid var(--mint-strong); border-radius:8px; padding:12px}
.muted{color:var(--muted)}
.accent{color:var(--mint-strong); font-weight:700}
.small{font-size:.9rem}
.stMarkdown hr{border-color:var(--line); margin:1.5rem 0}
.stButton>button{border:1px solid #d5dfd9; border-radius:7px; min-height:2.55rem; padding:0.45rem 1rem; background:var(--surface); color:var(--ink); font-weight:700; transition:all .18s ease}
.stButton>button:hover{border-color:var(--mint-strong); color:var(--mint-strong); transform:translateY(-1px); box-shadow:0 5px 14px rgba(22,122,90,.12)}
.stButton>button[kind='primary']{background:var(--mint-strong); border-color:var(--mint-strong); color:#fff}
.stButton>button[kind='primary']:hover{background:#0e6248; color:#fff}
.stTextInput>div>div>input, .stTextArea>div>div>textarea, .stSelectbox>div>div>div, .stMultiSelect>div>div>div{
  border-radius:7px !important; border-color:#d9e3dd !important; background:#fff !important; padding:8px !important;
}
.stTextInput>div>div>input:focus, .stTextArea>div>div>textarea:focus{border-color:var(--mint-strong) !important; box-shadow:0 0 0 1px var(--mint-strong) !important}
.stCheckbox label, .stRadio label{color:var(--ink)}
.stMetric{background:var(--surface); border:1px solid var(--line); border-radius:8px; padding:14px 16px; box-shadow:0 8px 22px rgba(31,45,38,.04)}
.stMetric label{color:var(--muted)}
.stMetric [data-testid='stMetricValue']{font-family:'Space Grotesk', sans-serif; color:var(--ink)}
.stDataFrame{border:1px solid var(--line); border-radius:8px; overflow:hidden}
section[data-testid='stSidebar']{background:#eef8f2; border-right:1px solid var(--line)}
section[data-testid='stSidebar'] h1, section[data-testid='stSidebar'] h2, section[data-testid='stSidebar'] h3{color:var(--ink)}
div[data-testid='stAlert']{border-radius:7px}
div[data-testid='stExpander']{border:1px solid var(--line); border-radius:8px; background:var(--surface)}
@media (max-width: 700px){
  .block-container{padding:1.4rem 1rem 3rem}
  .stApp h1{font-size:2rem}
  .page-header{margin-bottom:1rem}
}
</style>
"""

st.markdown(_TALENT_CSS, unsafe_allow_html=True)
apply_theme()

st.sidebar.markdown(
    """
    <div class="sidebar-brand">
      <span class="sidebar-brand-mark">T</span>
      <span class="sidebar-brand-name">Talent 360</span>
      <div class="sidebar-brand-caption">Talent operations OS</div>
    </div>
    """,
    unsafe_allow_html=True,
)

# Header
col1, col2 = st.columns([3,1])
with col1:
    st.markdown("""
    <div class="page-header home-hero">
      <div class="muted small" style="letter-spacing:.12em; text-transform:uppercase;">Talent intelligence / 01</div>
      <h2>Turn capability signals into growth.</h2>
      <div class="muted small">A governed operating system for requests, assessments, calibration, and development action.</div>
    </div>
    """, unsafe_allow_html=True)
with col2:
    st.markdown("""
    <div class='home-status' style='text-align:right; padding-top:1.65rem'>
      <div class='accent'>LIVE WORKFLOW</div>
      <div class='muted small'>08 connected workspaces</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

st.markdown("## Workflow journey")
st.markdown("Move one request through governed question supply, assessment, calibration, reassessment, and development action.")

steps = [
  ("01", "Employee Request", "Choose a person, mapped skill, and target level.", "var(--mint)", "◎"),
  ("02", "Question Supply", "Generate role-specific questions with a balanced difficulty mix.", "var(--blue)", "✦"),
  ("03", "Reviewer Approval", "Approve, reject, rewrite, or regenerate questions.", "var(--yellow)", "✓"),
  ("04", "Manager Assignment", "Select five approved questions with Easy, Medium, and Hard coverage.", "var(--blue)", "→"),
  ("05", "Employee Assessment", "Capture responses, score outcomes, and apply critical-question policy.", "var(--coral-soft)", "▣"),
  ("06", "Manager Review", "Validate evidence, sign off, calibrate, or send a failed result back.", "var(--mint)", "◈"),
  ("07", "Talent Dashboard", "Read portfolio signals, gaps, training actions, and the AI brief.", "var(--yellow)", "▤"),
  ("08", "Architecture + Data Map", "Trace governance decisions from workbook input to audit output.", "var(--coral-soft)", "⌘"),
]
for index in range(0, len(steps), 2):
  columns = st.columns(2)
  for column, step in zip(columns, steps[index:index + 2]):
    number, title, description, color, icon = step
    with column:
      st.markdown(
        f"""
        <div class='journey-card' style='background:{color}; border:1px solid rgba(23,32,42,.08); border-radius:8px; padding:18px; margin:0 0 14px;'>
          <div class='journey-icon' aria-hidden='true'>{icon}</div>
          <div style='font-family:"Space Grotesk",sans-serif; color:#52606d; font-size:.78rem; font-weight:700; letter-spacing:.08em;'>{number}</div>
          <div style='font-family:"Space Grotesk",sans-serif; color:#17202a; font-size:1.05rem; font-weight:700; margin:5px 0 4px;'>{title}</div>
          <div style='color:#52606d; font-size:.9rem;'>{description}</div>
        </div>
        """,
        unsafe_allow_html=True,
      )

st.info("Begin with Employee Request in the left navigation.")
st.warning(
  "Prototype mode: seeded demo identities are used for this local walkthrough. "
  "Production use requires authenticated role-based access, scoped data visibility, and transactional persistence."
)

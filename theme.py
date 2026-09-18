import streamlit as st


_THEME_CSS = r"""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Space+Grotesk:wght@500;600;700&display=swap');
:root {
  --ink: #17202a;
  --ink-soft: #52606d;
  --muted: #718096;
  --paper: #fbfcf8;
  --surface: #ffffff;
  --line: #e7ece7;
  --mint: #d9f4e8;
  --mint-strong: #167a5a;
  --coral: #f47b62;
  --coral-soft: #fff0eb;
  --blue: #dceeff;
  --blue-strong: #2867a8;
  --yellow: #fff2bd;
}

html, body, #root, .stApp { background: var(--paper) !important; }
.stApp { color: var(--ink); font-family: 'DM Sans', sans-serif; }
.stApp p, .stApp label, .stApp [data-testid='stWidgetLabel'],
.stApp [data-testid='stWidgetLabel'] p,
.stApp [data-testid='stWidgetLabel'] label { color: var(--ink) !important; }
.stApp h1, .stApp h2, .stApp h3, .stApp h4 {
  color: var(--ink);
  font-family: 'Space Grotesk', sans-serif;
  letter-spacing: 0;
}
.block-container { max-width: 1180px; padding: 2.25rem 3rem 4rem; }
.page-header {
  border-bottom: 1px solid var(--line);
  margin-bottom: 1.5rem;
  padding: 0 0 1.2rem;
  position: relative;
  animation: fade-up .5s ease-out both;
}
.page-header:before {
  background: var(--coral);
  border-radius: 3px;
  content: '';
  display: block;
  height: 5px;
  margin-bottom: 14px;
  width: 42px;
}
.page-header h2 { color: var(--ink); margin: 0; }
.page-header .muted { color: var(--ink-soft); margin-top: 5px; }
.muted { color: var(--muted); }
.small { font-size: .9rem; }
.journey-card, .architecture-layer, .governance-card {
  animation: fade-up .55s ease-out both;
  transition: box-shadow .2s ease, transform .2s ease;
}
.journey-card:hover, .architecture-layer:hover, .governance-card:hover {
  box-shadow: 0 12px 26px rgba(31, 45, 38, .10);
  transform: translateY(-3px);
}
.journey-card:nth-of-type(2), .architecture-layer:nth-of-type(2) { animation-delay: .08s; }
.journey-card:nth-of-type(3), .architecture-layer:nth-of-type(3) { animation-delay: .16s; }
.journey-icon {
  align-items: center;
  background: rgba(255, 255, 255, .72);
  border: 1px solid rgba(23, 32, 42, .10);
  border-radius: 7px;
  color: var(--ink);
  display: inline-flex;
  font-family: 'Space Grotesk', sans-serif;
  font-size: 1rem;
  font-weight: 700;
  height: 34px;
  justify-content: center;
  margin-bottom: 12px;
  width: 34px;
}
.architecture-arrow {
  animation: nudge-down 1.5s ease-in-out infinite;
  color: var(--coral);
  font-size: 1.25rem;
  margin: 0 0 8px 92px;
}
.data-map-panel {
  border: 1px solid var(--line);
  border-radius: 9px;
  box-shadow: 0 10px 30px rgba(31, 45, 38, .05);
  min-height: 190px;
  padding: 22px;
}
.data-map-source { background: linear-gradient(135deg, #eef8f2, #fff); border-top: 4px solid var(--mint-strong); }
.data-map-output { background: linear-gradient(135deg, #fff7dc, #fff); border-top: 4px solid #b47b16; }
.data-map-panel h3 { margin: 4px 0 2px; }
.data-map-panel p { color: var(--ink-soft); font-family: 'Space Grotesk', sans-serif; margin: 0; }
.data-map-panel strong { display: block; font-family: 'Space Grotesk', sans-serif; margin-bottom: 3px; }
.data-map-panel span { color: var(--ink-soft); display: block; line-height: 1.45; }
.data-map-panel small { color: var(--muted); display: block; margin-top: 15px; }
.data-map-kicker { color: var(--mint-strong); font-size: .72rem; font-weight: 700; letter-spacing: .12em; }
.data-map-output .data-map-kicker { color: #9a6810; }
.data-map-rule { border-top: 1px solid rgba(23, 32, 42, .12); margin: 16px 0 14px; }
.tab-row {
  border-bottom: 1px solid var(--line);
  display: flex;
  gap: 14px;
  min-height: 48px;
  padding: 10px 0;
}
.tab-name { color: var(--ink); flex: 0 0 38%; font-family: 'Space Grotesk', sans-serif; font-size: .84rem; font-weight: 700; }
.tab-description { color: var(--ink-soft); font-size: .86rem; line-height: 1.4; }
.output-row .tab-name { color: var(--blue-strong); }
.lineage-row {
  align-items: center;
  background: var(--surface);
  border: 1px solid var(--line);
  border-left: 5px solid var(--lineage-color);
  border-radius: 8px;
  box-shadow: 0 6px 18px rgba(31, 45, 38, .04);
  display: grid;
  gap: 15px;
  grid-template-columns: 38px 38px minmax(145px, .7fr) minmax(280px, 2fr);
  margin-bottom: 9px;
  padding: 13px 17px;
}
.lineage-icon { align-items: center; background: var(--lineage-color); border-radius: 7px; display: flex; font-size: 1rem; height: 32px; justify-content: center; width: 32px; }
.lineage-number { color: var(--muted); font-family: 'Space Grotesk', sans-serif; font-size: .78rem; font-weight: 700; letter-spacing: .08em; }
.lineage-title { color: var(--ink); font-family: 'Space Grotesk', sans-serif; font-weight: 700; }
.lineage-detail { color: var(--ink-soft); font-size: .86rem; line-height: 1.65; }
.lineage-detail span { color: var(--muted); display: inline-block; font-size: .68rem; font-weight: 700; letter-spacing: .1em; margin-right: 8px; min-width: 42px; }
@media (max-width: 760px) {
  .tab-row { display: block; }
  .tab-name { display: block; margin-bottom: 4px; }
  .lineage-row { align-items: start; grid-template-columns: 34px 34px 1fr; }
  .lineage-detail { grid-column: 1 / -1; }
}
.request-hero {
  align-items: flex-end;
  background: linear-gradient(120deg, #d9f4e8 0%, #eef8f2 58%, #fff0eb 100%);
  border: 1px solid rgba(22, 122, 90, .12);
  border-radius: 10px;
  display: flex;
  justify-content: space-between;
  margin: 0 0 1.4rem;
  overflow: hidden;
  padding: 24px 28px;
  position: relative;
}
.request-hero:after {
  border: 1px solid rgba(244, 123, 98, .28);
  border-radius: 50%;
  content: '';
  height: 160px;
  position: absolute;
  right: 30px;
  top: -85px;
  width: 160px;
}
.request-kicker {
  color: var(--mint-strong);
  font-size: .76rem;
  font-weight: 700;
  letter-spacing: .12em;
  text-transform: uppercase;
}
.request-hero h3 {
  font-size: 1.65rem;
  margin: 7px 0 5px;
  position: relative;
  z-index: 1;
}
.request-hero p { color: var(--ink-soft); margin: 0; max-width: 600px; position: relative; z-index: 1; }
.request-badge {
  align-items: center;
  background: rgba(255, 255, 255, .72);
  border: 1px solid rgba(23, 32, 42, .1);
  border-radius: 8px;
  color: var(--ink);
  display: flex;
  font-family: 'Space Grotesk', sans-serif;
  font-size: 1.1rem;
  font-weight: 700;
  gap: 8px;
  padding: 12px 14px;
  position: relative;
  z-index: 1;
}
.request-layout { margin-top: 4px; }
.request-panel, .request-profile {
  animation: fade-up .55s ease-out both;
  background: var(--surface);
  border: 1px solid var(--line);
  border-radius: 9px;
  box-shadow: 0 10px 30px rgba(31, 45, 38, .05);
  min-height: 250px;
  padding: 22px;
}
.request-profile { animation-delay: .1s; background: #f1f8f4; }
.request-panel h4, .request-profile h4 { margin: 0 0 5px; }
.request-panel .panel-caption, .request-profile .panel-caption { color: var(--muted); font-size: .88rem; margin-bottom: 18px; }
.profile-label { color: var(--muted); font-size: .76rem; font-weight: 700; letter-spacing: .08em; margin-top: 18px; text-transform: uppercase; }
.profile-value { color: var(--ink); font-family: 'Space Grotesk', sans-serif; font-size: 1rem; font-weight: 600; line-height: 1.35; }
.request-rail { display: flex; gap: 6px; margin: 0 0 1.4rem; }
.request-rail span { background: var(--line); border-radius: 4px; color: var(--muted); flex: 1; font-size: .72rem; font-weight: 700; padding: 7px 9px; text-align: center; }
.request-rail span.active { background: var(--mint-strong); color: #fff; }
.request-next { border-left: 3px solid var(--coral); margin-top: 22px; padding-left: 12px; }
.request-next strong { color: var(--ink); display: block; font-family: 'Space Grotesk', sans-serif; font-size: .92rem; }
.request-next span { color: var(--ink-soft); font-size: .86rem; }
.stButton > button {
  background: var(--surface);
  border: 1px solid #d5dfd9;
  border-radius: 7px;
  color: var(--ink);
  font-weight: 700;
  min-height: 2.55rem;
  padding: .45rem 1rem;
}
.stButton > button:hover {
  border-color: var(--mint-strong);
  box-shadow: 0 5px 14px rgba(22, 122, 90, .12);
  color: var(--mint-strong);
  transform: translateY(-1px);
}
.stTextInput > div > div > input,
.stTextArea > div > div > textarea,
.stSelectbox > div > div > div,
.stMultiSelect > div > div > div {
  background: #fff !important;
  border: 1px solid #d9e3dd !important;
  border-radius: 7px !important;
  padding: 8px !important;
}
[data-baseweb='select'] > div {
  background: #fff !important;
  border-color: #d9e3dd !important;
  color: var(--ink) !important;
}
[data-baseweb='select'] span,
[data-baseweb='select'] div,
[data-baseweb='select'] input { color: var(--ink) !important; }
.stSelectbox svg, .stMultiSelect svg { fill: var(--ink-soft) !important; }
.stSelectbox [role='combobox'], .stMultiSelect [role='combobox'] {
  background: #fff !important;
  border: 0 !important;
  color: var(--ink) !important;
}
.stSelectbox [role='group'], .stMultiSelect [role='group'] {
  background: #fff !important;
  border: 1px solid #d9e3dd !important;
  border-radius: 7px !important;
}
.stSelectbox [role='combobox']::placeholder,
.stMultiSelect [role='combobox']::placeholder { color: var(--muted) !important; }
.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {
  border-color: var(--mint-strong) !important;
  box-shadow: 0 0 0 1px var(--mint-strong) !important;
}
.stMetric {
  background: var(--surface);
  border: 1px solid var(--line);
  border-radius: 8px;
  box-shadow: 0 8px 22px rgba(31, 45, 38, .04);
  padding: 14px 16px;
}
.stMetric label { color: var(--muted); }
.stMetric [data-testid='stMetricValue'] {
  color: var(--ink);
  font-family: 'Space Grotesk', sans-serif;
}
.stDataFrame { border: 1px solid var(--line); border-radius: 8px; overflow: hidden; }
section[data-testid='stSidebar'] {
  background: #eef8f2;
  border-right: 1px solid var(--line);
}
section[data-testid='stSidebar'] h1,
section[data-testid='stSidebar'] h2,
section[data-testid='stSidebar'] h3 { color: var(--ink); }
section[data-testid='stSidebar'] [data-testid='stSidebarNav'] { padding-top: 1rem; }
section[data-testid='stSidebar'] [data-testid='stSidebarNav'] a {
  background: transparent !important;
  border-left: 3px solid transparent;
  border-radius: 0 7px 7px 0;
  color: var(--ink-soft) !important;
  margin: 3px 0;
  padding: 9px 12px;
}
section[data-testid='stSidebar'] [data-testid='stSidebarNav'] a:hover {
  background: rgba(217, 244, 232, .8) !important;
  color: var(--mint-strong) !important;
}
section[data-testid='stSidebar'] [data-testid='stSidebarNav'] a[aria-current='page'] {
  background: var(--mint) !important;
  border-left-color: var(--coral);
  color: var(--ink) !important;
  font-weight: 700;
}
section[data-testid='stSidebar'] [data-testid='stSidebarNav'] a[aria-current='page'] *,
section[data-testid='stSidebar'] [data-testid='stSidebarNav'] a * {
  color: inherit !important;
}
/* Keep app.py as the launch target while presenting a product name in navigation. */
section[data-testid='stSidebar'] [data-testid='stSidebarNav'] ul > li:first-child a {
  font-size: 0 !important;
}
section[data-testid='stSidebar'] [data-testid='stSidebarNav'] ul > li:first-child a::after {
  color: var(--ink-soft) !important;
  content: 'Talent 360';
  font-size: .9rem;
}
section[data-testid='stSidebar'] [data-testid='stSidebarNav'] ul > li:first-child a[aria-current='page']::after {
  color: var(--ink) !important;
  font-weight: 700;
}
div[data-testid='stAlert'], div[data-testid='stExpander'] { border-radius: 7px; }
[data-testid='stBaseButton-primary'] {
  background: var(--mint-strong) !important;
  border-color: var(--mint-strong) !important;
  color: #fff !important;
}
[data-testid='stBaseButton-primary']:hover {
  background: #0e6248 !important;
  color: #fff !important;
}
@keyframes fade-up {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}
@keyframes nudge-down {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(4px); }
}
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: .01ms !important;
    animation-iteration-count: 1 !important;
    scroll-behavior: auto !important;
    transition-duration: .01ms !important;
  }
}
@media (max-width: 700px) {
  .block-container { padding: 1.4rem 1rem 3rem; }
  .page-header { margin-bottom: 1rem; }
  .request-hero { align-items: flex-start; flex-direction: column; gap: 16px; }
  .request-badge { font-size: .95rem; }
}

/* Command-center layer: shared presentation only; page logic remains unchanged. */
:root {
  --ink: #172235;
  --ink-soft: #58677a;
  --muted: #8190a2;
  --paper: #f5f7f4;
  --surface: #ffffff;
  --line: #dfe6e1;
  --mint: #d9f4e8;
  --mint-strong: #087f66;
  --coral: #f1745f;
  --coral-soft: #fff0eb;
  --blue: #e5efff;
  --blue-strong: #2b5fa8;
  --yellow: #fff1bd;
  --navy: #172235;
  --lime: #c8ef83;
}
html, body, #root, .stApp {
  background:
    radial-gradient(circle at 78% -12%, rgba(200,239,131,.30), transparent 29rem),
    linear-gradient(135deg, #f9fbf8 0%, #f3f6f4 52%, #eef3f4 100%) !important;
}
.stApp { min-height: 100vh; }
.block-container {
  max-width: 1280px;
  padding: 2.4rem 4.2rem 5rem;
}
.page-header {
  border: 1px solid rgba(223,230,225,.9);
  border-radius: 18px;
  background: rgba(255,255,255,.70);
  box-shadow: 0 16px 45px rgba(23,34,53,.06);
  margin-bottom: 1.4rem;
  padding: 1.65rem 1.8rem 1.45rem;
  backdrop-filter: blur(12px);
}
.page-header:before { background: var(--lime); height: 7px; width: 52px; }
.page-header h2 { font-size: clamp(1.75rem, 3vw, 2.75rem); letter-spacing: -.03em; }
.page-header .muted { font-size: .98rem; }
.audience-banner {
  border-radius: 16px !important;
  box-shadow: 0 12px 30px rgba(23,34,53,.05);
  padding: 17px 20px !important;
}
.audience-icon { border-radius: 10px !important; box-shadow: 0 5px 12px rgba(23,34,53,.12); }
.card, .kpi, .request-panel, .request-profile, .data-map-panel {
  border-color: rgba(223,230,225,.95);
  border-radius: 16px;
  box-shadow: 0 14px 36px rgba(23,34,53,.06);
}
.stMetric {
  border: 1px solid rgba(223,230,225,.95);
  border-radius: 14px;
  box-shadow: 0 10px 26px rgba(23,34,53,.06);
  min-height: 104px;
}
.stMetric [data-testid='stMetricValue'] { font-size: 1.7rem; letter-spacing: -.03em; }
.stDataFrame { border-radius: 14px; box-shadow: 0 12px 28px rgba(23,34,53,.05); }
.stButton > button {
  border-radius: 10px;
  min-height: 2.8rem;
  transition: transform .18s ease, box-shadow .18s ease, border-color .18s ease;
}
.stButton > button:hover { transform: translateY(-2px); box-shadow: 0 9px 20px rgba(23,34,53,.12); }
section[data-testid='stSidebar'] {
  background: linear-gradient(180deg, #162236 0%, #1c2b40 62%, #20364a 100%);
  border-right: 0;
  box-shadow: 12px 0 35px rgba(23,34,53,.12);
}
section[data-testid='stSidebar'] [data-testid='stSidebarNav'] { padding: 5.6rem .8rem 1.5rem; }
section[data-testid='stSidebar'] [data-testid='stSidebarNav'] a {
  border-left: 3px solid transparent;
  border-radius: 11px;
  color: #b8c8d8 !important;
  margin: 4px 0;
  padding: 11px 13px;
  transition: background .18s ease, color .18s ease, transform .18s ease;
}
section[data-testid='stSidebar'] [data-testid='stSidebarNav'] a:hover {
  background: rgba(200,239,131,.12) !important;
  color: #fff !important;
  transform: translateX(3px);
}
section[data-testid='stSidebar'] [data-testid='stSidebarNav'] a[aria-current='page'] {
  background: rgba(200,239,131,.16) !important;
  border-left-color: var(--lime);
  color: #fff !important;
}
section[data-testid='stSidebar'] [data-testid='stSidebarNav'] a * { color: inherit !important; }
section[data-testid='stSidebar'] [data-testid='stSidebarUserContent'] { padding-top: 1rem; }
.sidebar-brand {
  color: #fff;
  left: 1.25rem;
  position: absolute;
  top: 1.35rem;
  z-index: 5;
}
.sidebar-brand-mark {
  align-items: center;
  background: var(--lime);
  border-radius: 10px;
  color: var(--navy);
  display: inline-flex;
  font-family: 'Space Grotesk', sans-serif;
  font-size: 1.05rem;
  font-weight: 700;
  height: 34px;
  justify-content: center;
  margin-right: 9px;
  width: 34px;
}
.sidebar-brand-name { font-family: 'Space Grotesk', sans-serif; font-size: 1rem; font-weight: 700; }
.sidebar-brand-caption { color: #8ea3b8; font-size: .68rem; letter-spacing: .12em; margin: 4px 0 0 43px; text-transform: uppercase; }
.stTextInput > div > div > input,
.stTextArea > div > div > textarea,
.stSelectbox > div > div > div,
.stMultiSelect > div > div > div { border-radius: 10px !important; }
@media (max-width: 700px) {
  .block-container { padding: 1.25rem 1rem 3rem; }
  .page-header { border-radius: 14px; padding: 1.25rem; }
  section[data-testid='stSidebar'] [data-testid='stSidebarNav'] { padding-top: 5rem; }
}
</style>
"""


_AUDIENCE_STYLES = {
  "employee": ("#167a5a", "#d9f4e8", "#f47b62"),
  "manager": ("#2867a8", "#dceeff", "#167a5a"),
  "governance": ("#9a6715", "#fff2bd", "#2867a8"),
  "analytics": ("#5f4b8b", "#eee8ff", "#f47b62"),
  "neutral": ("#52606d", "#eef2f4", "#f47b62"),
}


def apply_theme(audience="neutral"):
  """Load the shared UI and a small visual treatment for the page audience."""
  primary, soft, accent = _AUDIENCE_STYLES.get(audience, _AUDIENCE_STYLES["neutral"])
  audience_css = f"""
  <style>
  :root {{ --audience-primary: {primary}; --audience-soft: {soft}; --audience-accent: {accent}; }}
  .audience-banner {{ border-left-color: var(--audience-accent) !important; background: var(--audience-soft) !important; }}
  .audience-banner .audience-kicker {{ color: var(--audience-primary) !important; }}
  .audience-banner .audience-icon {{ background: var(--audience-primary) !important; }}
  .audience-banner .audience-copy {{ color: var(--ink-soft) !important; }}
  .audience-section-title {{ color: var(--audience-primary) !important; }}
    .stButton > button[kind='primary'], [data-testid='stBaseButton-primary'] {{
      background: var(--audience-primary) !important;
      border-color: var(--audience-primary) !important;
    }}
    .stButton > button[kind='primary']:hover, [data-testid='stBaseButton-primary']:hover {{
      filter: brightness(.92);
    }}
  </style>
  """
  st.markdown(_THEME_CSS + audience_css, unsafe_allow_html=True)


def audience_banner(audience, title, description, icon):
  """Render a compact audience cue below a page header."""
  labels = {
    "employee": "Your development journey",
    "manager": "Manager workspace",
    "governance": "Governance workspace",
    "analytics": "Talent intelligence",
    "neutral": "Workflow guide",
  }
  label = labels.get(audience, labels["neutral"])
  st.markdown(
    f"""
    <div class="audience-banner" style="align-items:center; border-left:4px solid; border-radius:8px; display:flex; gap:14px; margin:0 0 1.4rem; padding:14px 17px;">
      <div class="audience-icon" style="align-items:center; border-radius:7px; color:#fff; display:flex; font-family:'Space Grotesk',sans-serif; font-size:1.05rem; font-weight:700; height:34px; justify-content:center; width:34px;">{icon}</div>
      <div>
        <div class="audience-kicker" style="font-size:.73rem; font-weight:700; letter-spacing:.1em; text-transform:uppercase;">{label}</div>
        <div style="color:var(--ink); font-family:'Space Grotesk',sans-serif; font-size:1rem; font-weight:700; margin-top:3px;">{title}</div>
        <div class="audience-copy" style="font-size:.86rem; margin-top:2px;">{description}</div>
      </div>
    </div>
    """,
    unsafe_allow_html=True,
  )

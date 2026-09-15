import json
from datetime import datetime

import streamlit as st

from ai import generate_questions
from db import append_output_row, load_input_sheet
from utils import parse_questions, validate_question
from theme import apply_theme, audience_banner
from workflow import effective_question_bank

apply_theme("governance")

st.markdown("""
<div class="page-header">
    <h2>6. Admin Question Bank</h2>
    <div class="muted small">Generate draft questions for SME review</div>
</div>
""", unsafe_allow_html=True)
audience_banner("governance", "Build a trusted question supply", "Generate drafts, then send them through SME review before scheduling.", "✦")

roles = load_input_sheet("Role_Master")
blueprints = load_input_sheet("Assessment_Blueprints")
role_skills = load_input_sheet("Role_Skill_Map")
levels = load_input_sheet("Proficiency_Levels")
question_bank = effective_question_bank()
expected = (
    blueprints[["blueprint_id", "role_id"]]
    .merge(role_skills[["role_id", "skill_id", "skill"]], on="role_id", how="inner")
    .merge(roles[["role_id", "role_name"]], on="role_id", how="left")
    [["role_id", "role_name", "blueprint_id", "skill_id", "skill"]]
    .drop_duplicates()
)
if question_bank.empty:
    summary = expected
    summary["generated"] = 0
    summary["approved"] = 0
    summary["pending_review"] = 0
else:
    inventory = question_bank.copy()
    inventory["generated"] = inventory["question_id"].astype(str).str.startswith("Q-AI-")
    inventory["approved"] = (
        (inventory["sme_review_status"] == "Approved") &
        (inventory["approved_for_schedule"] == "Yes")
    )
    inventory["pending_review"] = inventory["sme_review_status"] != "Approved"
    counts = (
        inventory.groupby(
            ["role_id", "role_name", "blueprint_id", "skill_id", "skill"],
            dropna=False,
        )
        .agg(
            generated=("generated", "sum"),
            approved=("approved", "sum"),
            pending_review=("pending_review", "sum"),
        )
        .reset_index()
    )
    summary = expected.merge(
        counts,
        on=["role_id", "role_name", "blueprint_id", "skill_id", "skill"],
        how="left",
    )
    summary[["generated", "approved", "pending_review"]] = summary[
        ["generated", "approved", "pending_review"]
    ].fillna(0).astype(int)
    summary["need_to_generate"] = (5 - summary["generated"]).clip(lower=0)
    summary["need_approval"] = (5 - summary["approved"]).clip(lower=0)
summary["need_to_generate"] = (5 - summary["generated"]).clip(lower=0)
summary["need_approval"] = (5 - summary["approved"]).clip(lower=0)
summary["next_action"] = "Ready for assignment"
summary.loc[summary["need_approval"] > 0, "next_action"] = "Approve questions"
summary.loc[summary["need_to_generate"] > 0, "next_action"] = "Generate questions"
summary = summary.rename(
    columns={
        "role_id": "Role",
        "role_name": "Role name",
        "blueprint_id": "Blueprint",
        "skill_id": "Skill ID",
        "skill": "Skill",
        "generated": "Generated",
        "approved": "Approved",
        "pending_review": "Pending review",
        "need_to_generate": "Need to generate",
        "need_approval": "Need approval",
        "next_action": "Next action",
    }
)
generation_gap = int(summary["Need to generate"].sum())
generation_targets = int((summary["Need to generate"] > 0).sum())
approval_gap = int(summary["Need approval"].sum())
approval_targets = int((summary["Need approval"] > 0).sum())
generated_total = int(summary["Generated"].sum())
approved_total = int(summary["Approved"].sum())
pending_total = int(summary["Pending review"].sum())

st.subheader("Question supply overview")
st.caption("Each blueprint and skill needs five approved questions before a manager can assign an assessment.")
metric_columns = st.columns(5)
metric_columns[0].metric("Need to generate", generation_gap, f"{generation_targets} skill sets")
metric_columns[1].metric("Need approval", approval_gap, f"{approval_targets} skill sets")
metric_columns[2].metric("Generated", generated_total, "AI-created questions")
metric_columns[3].metric("Approved", approved_total, "Ready to assign")
metric_columns[4].metric("Pending review", pending_total, "Awaiting SME")

action_queue = summary[
    (summary["Need to generate"] > 0) | (summary["Need approval"] > 0)
].copy()
action_queue["Need to generate"] = action_queue["Need to generate"].astype(int)
action_queue = action_queue.sort_values(
    ["Need to generate", "Need approval"], ascending=[False, False]
)
st.markdown("#### Start here")
if action_queue.empty:
    st.success("Every blueprint and skill has at least five generated questions.")
else:
    st.warning(
        f"{generation_gap} questions still need to be generated across {generation_targets} skill sets."
    )
    st.dataframe(
        action_queue[
            [
                "Role name",
                "Blueprint",
                "Skill",
                "Generated",
                "Approved",
                "Pending review",
                "Need to generate",
                "Next action",
            ]
        ],
        column_config={
            "Role name": st.column_config.TextColumn("Role", width="medium"),
            "Blueprint": st.column_config.TextColumn("Blueprint", width="small"),
            "Skill": st.column_config.TextColumn("Skill", width="medium"),
            "Generated": st.column_config.NumberColumn("Generated", width="small"),
            "Approved": st.column_config.NumberColumn("Approved", width="small"),
            "Pending review": st.column_config.NumberColumn("Pending", width="small"),
            "Need to generate": st.column_config.NumberColumn("Need", width="small"),
            "Next action": st.column_config.TextColumn("Next action", width="medium"),
        },
        hide_index=True,
        width="stretch",
        height=min(430, len(action_queue) * 38 + 40),
    )

with st.expander("View complete inventory"):
    st.dataframe(
        summary[
            [
                "Role",
                "Role name",
                "Blueprint",
                "Skill ID",
                "Skill",
                "Generated",
                "Approved",
                "Pending review",
                "Need to generate",
                "Need approval",
                "Next action",
            ]
        ],
        hide_index=True,
        width="stretch",
    )

st.divider()
st.subheader("Generate questions")

role_id = st.selectbox(
    "Role",
    roles["role_id"].tolist(),
    format_func=lambda value: roles.loc[roles["role_id"] == value, "role_name"].iloc[0],
)
role_blueprints = blueprints[blueprints["role_id"] == role_id]
blueprint_id = st.selectbox(
    "Blueprint",
    role_blueprints["blueprint_id"].tolist(),
    format_func=lambda value: role_blueprints.loc[
        role_blueprints["blueprint_id"] == value, "assessment_name"
    ].iloc[0],
)
role_skill_rows = role_skills[role_skills["role_id"] == role_id].drop_duplicates("skill_id")
skill_id = st.selectbox(
    "Skill",
    role_skill_rows["skill_id"].tolist(),
    format_func=lambda value: role_skill_rows.loc[
        role_skill_rows["skill_id"] == value, "skill"
    ].iloc[0],
)
target_level = st.selectbox(
    "Target Level",
    levels["level"].tolist(),
    format_func=lambda value: levels.loc[levels["level"] == value, "level_name"].iloc[0],
)

if st.button("Generate Question Bank"):
    skill_name = role_skill_rows.loc[role_skill_rows["skill_id"] == skill_id, "skill"].iloc[0]
    raw = generate_questions(skill_name, str(target_level), count=10)
    try:
        questions = parse_questions(raw)
        for question in questions:
            validate_question(question)
        for question in questions:
            options = question["options"]
            answer = question["answer"]
            correct_option = ["A", "B", "C", "D"][options.index(answer)]
            append_output_row(
                "Assessment_QBank",
                {
                    "question_id": f"Q-AI-{datetime.now().strftime('%Y%m%d%H%M%S%f')}",
                    "blueprint_id": blueprint_id,
                    "data_label": "Application-created record",
                    "tower": roles.loc[roles["role_id"] == role_id, "tower"].iloc[0],
                    "role_id": role_id,
                    "role_name": roles.loc[roles["role_id"] == role_id, "role_name"].iloc[0],
                    "skill_id": skill_id,
                    "skill": skill_name,
                    "target_proficiency_level": target_level,
                    "question_source": "AI-generated from role and skill definition",
                    "source_question_reference": "",
                    "question_type": "Multiple Choice - Scenario",
                    "question_text": question["question"],
                    "option_a": options[0],
                    "option_b": options[1],
                    "option_c": options[2],
                    "option_d": options[3],
                    "correct_option": correct_option,
                    "critical_flag": "No",
                    "difficulty": question.get("difficulty", "Medium"),
                    "ai_confidence": "",
                    "sme_review_status": "Pending SME Review",
                    "sme_action_required": "Review",
                    "approved_for_schedule": "No",
                    "schedule_scope": "",
                    "generated_prompt_context": json.dumps({"skill": skill_name, "level": target_level}),
                    "eligible_formula_note": "Requires SME approval before scheduling",
                },
            )
        st.success(f"{len(questions)} draft questions created and sent for SME review.")
    except Exception as error:
        st.error(f"Unable to save the generated question bank: {error}")

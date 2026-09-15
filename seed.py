# seed.py
import pandas as pd

excel_path = "Talent360i_Auto_Assessment_Hackfest_Dataset_v2.xlsx"

# Define empty DataFrames for required sheets
questions = pd.DataFrame(columns=[
    "id", "skill", "level", "content", "status",
    "created_by", "model", "prompt_version",
    "created_at", "reviewed_by", "reviewed_at"
])

assessments = pd.DataFrame(columns=[
    "id", "employee", "skill", "requested_level",
    "status", "selected_questions", "answers",
    "evidence", "score", "current_level",
    "training_need", "study_plan", "manager_note",
    "created_at", "updated_at", "submitted_at"
])

audit_log = pd.DataFrame(columns=[
    "id", "entity_type", "entity_id", "action",
    "actor", "details", "created_at"
])

# Write all sheets to Excel
with pd.ExcelWriter(excel_path, engine="openpyxl") as writer:
    questions.to_excel(writer, sheet_name="questions", index=False)
    assessments.to_excel(writer, sheet_name="assessments", index=False)
    audit_log.to_excel(writer, sheet_name="audit_log", index=False)

print("✅ Excel initialized with required sheets.")

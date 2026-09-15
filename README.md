# Talent 360

Talent 360 is a Streamlit prototype for governed, AI-assisted employee skill assessment. The active application uses Excel workbooks as its persistence layer and combines seeded reference data with application-created assessment records.

The canonical source is the repository root (`app.py`, `pages/`, and the shared Python modules). The nested `11. talent 360/` directory, SQLite-oriented modules, and older seed/validation paths are legacy material unless explicitly migrated.

## Architecture

- **UI:** Streamlit numbered pages under `pages/`.
- **Reference data:** `Talent360i_Input_Dataset.xlsx`, loaded read-only with pandas.
- **Application data:** `Talent360i_Output.xlsx`, created as a copy of the input workbook on first write.
- **Workbook access:** `db.py` reads and replaces individual tabs with pandas and openpyxl.
- **Workflow rules:** `workflow.py` merges input question data with the latest output review decisions.
- **AI generation:** `ai.py` calls OpenAI and expects JSON multiple-choice questions.
- **Validation:** `utils.py` parses and validates generated questions.

The input workbook must contain the reference tabs used by the pages, including `Users_Teams`, `Role_Master`, `Role_Skill_Map`, `Proficiency_Levels`, `Assessment_Blueprints`, `Assessment_Schedules`, `Assessment_QBank`, `Assessment_Results`, `User_Skill_Assessments`, `Skill_Gaps_TNI`, and `Training_Skill_Map`.

## End-to-End Workflow

1. **Employee Request** (`pages/1_Employee_Request.py`)
   - Select a seeded user, role-mapped skill, and target proficiency level.
   - Append an `Assessment_Requests` row with status `Requested`.
   - Append the request event to `App_Audit_Log`.

2. **Manager Assignment** (`pages/2_Manager_Assignment.py`)
   - Select a blueprint for the employee's role.
   - Find approved questions for the blueprint and skill, falling back to approved questions from the blueprint when necessary.
   - Select five questions and create `Assessment_Assignments` plus `Assessment_Assignment_Questions` rows.
   - The request status changes to `Assigned`.
   - Assignment uses the first available schedule, preferring `Ready to Schedule`.

3. **Reviewer Approval** (`pages/3_Reviewer_Approval.py`)
   - Select pending questions individually.
   - Record approval in `SME_Review_Workflow` with reviewer role, decision, review date, and human-in-the-loop completion.
   - Only questions with effective status `Approved` and `approved_for_schedule == Yes` are assignable.

4. **Employee Assessment** (`pages/4_Employee_Assessment.py`)
   - Select an employee and an incomplete assignment.
   - Answer the assigned questions only.
   - Record each response in `Assessment_Responses`.
   - Calculate a percentage score and critical-question failure.
   - Write an `Assessment_Results` row with status `Scored`; mark the assignment `Completed`.

5. **Manager Review** (`pages/5_Manager_Review.py`)
   - Review scored results and choose a calibrated proficiency level.
   - Change the result status to `Calibrated`.
   - Write `User_Skill_Assessments` and `Skill_Gaps_TNI` records using the role target level and `Training_Skill_Map`.

6. **Admin Question Bank** (`pages/6_Admin_Question_Bank.py`)
   - Generate ten questions for a role, blueprint, skill, and target level.
   - Save each question to `Assessment_QBank` as `Pending SME Review` and `approved_for_schedule == No`.
   - Reviewers must approve generated questions before assignment.

7. **Talent Dashboard** (`pages/7_Dashboard.py`)
   - Combine reference and application-created results, skill assessments, and gaps.
   - Show assessment counts, scored/calibrated results, skill levels, high gaps, and training recommendations.

## Scoring Rules

- `score_pct` is the percentage of assigned questions answered correctly.
- The pass threshold is `75` percent.
- A question with `critical_flag == Yes` answered incorrectly sets `critical_fail_flag` to `Yes` and causes a fail regardless of percentage.
- The stored recommendation is `min(5, int(score_pct // 20))`.
- Managers can calibrate the recommended level before downstream skill-gap records are created.

## Output Tabs

The application creates or updates these tabs in `Talent360i_Output.xlsx`: `Assessment_Requests`, `Assessment_Assignments`, `Assessment_Assignment_Questions`, `Assessment_Responses`, `Assessment_Results`, `SME_Review_Workflow`, `User_Skill_Assessments`, `Skill_Gaps_TNI`, and `App_Audit_Log`.

## Running Locally

Place the input workbook in the project directory, then run:

```powershell
.\.venv\Scripts\Activate.ps1
streamlit run app.py
```

Open the local URL shown by Streamlit, normally `http://localhost:8501`.

For AI question generation, create `.env` with:

```text
OPENAI_API_KEY=your-openai-api-key
```

The configured model is `gpt-4` and the prompt version is `v2`. Never commit `.env`, API keys, or generated output workbooks containing sensitive data.

## Demo Walkthrough

1. Start the app and open `1. Employee Request`.
2. Select a seeded user, mapped skill, and target level; submit the request.
3. If fewer than five approved questions exist, use `6. Admin Question Bank` to generate ten questions.
4. Open `3. Reviewer Approval` and approve at least five suitable questions.
5. Open `2. Manager Assignment`, choose a blueprint, select five questions, and assign the assessment.
6. Open `4. Employee Assessment`, select the user and assignment, answer every question, and submit.
7. Open `5. Manager Review`, choose the calibrated level, and confirm it.
8. Open `7. Dashboard` to inspect results, skill gaps, and training recommendations.

## Validation and Legacy Notes

Run `python -m py_compile app.py db.py workflow.py ai.py utils.py pages/*.py` to catch syntax errors. `validate.py`, `seed.py`, `models.py`, and `services.py` contain older SQLite or separate-workbook assumptions and should not be treated as the active workflow contract without review. The current pages do not implement duplicate-request prevention, evidence capture, expiry enforcement, question-bank rejection, manager send-back, or study-plan persistence.

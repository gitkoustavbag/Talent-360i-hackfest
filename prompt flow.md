# Talent 360 Prompt Flow

This is the implementation and maintenance specification for the active Talent 360 application. It describes the workbook-backed Streamlit architecture in the repository root. Use the prompts in order for a rebuild or use only the relevant prompt when changing an existing page. Do not reintroduce the older SQLite contract unless the whole application is deliberately migrated.

## Prompt 1: Create The Project

```text
Inspect the existing Talent 360 workspace before editing. Treat the repository-root Streamlit pages and shared modules as the active surface.

Use this structure:
- app.py
- ai.py
- db.py
- models.py
- utils.py
- seed.py
- services.py
- requirements.txt
- pages/1_Employee_Request.py
- pages/2_Manager_Assignment.py
- pages/3_Reviewer_Approval.py
- pages/4_Employee_Assessment.py
- pages/5_Manager_Review.py
- pages/6_Admin_Question_Bank.py
- pages/7_Dashboard.py

Use Streamlit, pandas, and openpyxl. Preserve the workbook architecture and inspect `Talent360i_Input_Dataset.xlsx` before changing schema assumptions. Create `Talent360i_Output.xlsx` by copying the input workbook on first write. Do not invent SQLite tables, SQL migrations, or a second frontend.

Before editing, inspect the workspace. After editing, compile all Python files and report any errors.
```

## Prompt 2: Implement Workbook Persistence

```text
Implement `db.py` as a small workbook repository. Define input/output paths, copy the input workbook on first write, clean title/metadata rows when reading, return empty optional output tabs, append rows without changing unrelated tabs, and replace only the requested output tab with openpyxl. Keep legacy helpers only when existing pages still import them; do not document them as SQL transactions. Never reset a user's output workbook.
```

## Prompt 3: Add AI And Question Validation

```text
Implement `ai.py` and `utils.py`.

ai.py must:
- load OPENAI_API_KEY from .env
- expose generate_questions(skill, level, count=10)
- ask the model for a JSON array of multiple-choice questions
- require each question to contain id, question, options, answer, difficulty, and rationale
- use the configured chat-completions API
- expose `MODEL = "gpt-4"` and `PROMPT_VERSION = "v2"`

utils.py must:
- expose parse_questions(data)
- support Python lists, plain JSON strings, and Markdown-fenced JSON strings such as ```json ... ```
- accept a JSON object containing a `questions` array as well as a direct array
- reject empty or non-array question banks with a clear ValueError
- validate exactly four non-empty options, a valid answer index or answer option, non-empty difficulty, and unique question IDs
- validate each question's required fields, four options, and exact answer text
- retain small validation helpers where useful

Do not silently swallow malformed AI responses. Add a focused test or one-off command for fenced JSON parsing.
```

## Prompt 4: Build The Employee Request Page

```text
Create pages/1_Employee_Request.py.

The page must:
- be titled "1. Employee Request"
- select a seeded user from `Users_Teams`
- derive skills from `Role_Skill_Map`
- select a level from `Proficiency_Levels`
- append an `Assessment_Requests` row with status `Requested`
- append an `App_Audit_Log` event named `requested`

The request page must not display assessment questions. It is only the start of the employee journey.
```

## Prompt 5: Build Manager Assignment

```text
Create pages/2_Manager_Assignment.py.

For each request with status `Requested`, show employee, role, skill, and target level; select a role-compatible blueprint; use `workflow.effective_question_bank()`; prefer approved questions matching blueprint and skill, falling back to approved blueprint questions when necessary; require exactly five; choose a schedule, preferring `Ready to Schedule`; create `Assessment_Assignments` and `Assessment_Assignment_Questions`; and change the request status to `Assigned`.

Do not combine historical question banks. Use only the latest approved matching bank for selection.
```

## Prompt 6: Build Reviewer Approval

```text
Create pages/3_Reviewer_Approval.py.

Show pending questions from `Assessment_QBank` after applying `workflow.effective_question_bank()`. Allow individual selection, collect reviewer role, and write one `SME_Review_Workflow` row per approved question with status `Approved`, decision `Approve`, review date, and human-in-the-loop completion.

Only questions with effective status `Approved` and `approved_for_schedule == Yes` may be assigned. The active page supports approval, not rejection. Show errors clearly.
```

## Prompt 7: Build Employee Assessment

```text
Create pages/4_Employee_Assessment.py.

The page must:
- select an employee from `Users_Teams`
- list that employee's assignments whose status is not `Completed`
- let the employee choose one assigned assessment
- load question IDs from `Assessment_Assignment_Questions`
- display only assigned questions from `effective_question_bank()`
- record `Assessment_Responses`, calculate percentage and critical failure, write an `Assessment_Results` row with status `Scored`, and mark the assignment `Completed`

Never query and merge all approved questions directly on this page.
```

## Prompt 8: Build Manager Review And Skill Gaps

```text
Create pages/5_Manager_Review.py.

For each `Assessment_Results` row with status `Scored`, show score, pass/fail, critical failure, and recommendation; allow a calibrated level; set status `Calibrated`; calculate the gap from the role-skill target; classify it as `No gap`, `Moderate`, or `High`; find a mapped course in `Training_Skill_Map`; and write `User_Skill_Assessments` plus `Skill_Gaps_TNI` rows.

Persist calibration, skill-gap, and training-recommendation records in the output workbook so they appear on the Dashboard.
```

## Prompt 9: Build Admin And Dashboard

```text
Create pages/6_Admin_Question_Bank.py and pages/7_Dashboard.py.

Admin Question Bank:
- provide role, blueprint, skill, and level dropdowns
- generate exactly 10 questions
- parse and validate the AI response
- append each question to `Assessment_QBank` as `Pending SME Review` with `approved_for_schedule == No`
- explain that SME approval is required

Dashboard:
- combine input and output rows for results, skill assessments, and gaps
- show counts for assessments, scored results, calibrated results, and high gaps
- show results, calibrated skill levels, gaps, and training recommendations
- use pandas for tabular data

These pages are supporting pages. They must not replace the employee-first journey.
```

## Prompt 10: Update The Home Page

```text
Update app.py so the home page clearly explains the numbered journey:
1. Employee Request
2. Manager Assignment
3. Reviewer Approval
4. Employee Assessment
5. Manager Review
6. Admin Question Bank
7. Talent Dashboard

Tell users to begin with Employee Request. Explain seeded workbook data, role mappings, SME approval, five-question assignments, scoring, calibration, and dashboard gap reporting. Keep the home page informational and do not duplicate workflow logic there.
```

## Prompt 11: Validate The Whole Project

```text
Validate the completed Talent 360 Streamlit project.

Run:
- Python compilation for every .py file
- static diagnostics for all active pages
- workbook existence and required-tab checks
- a parser test for Markdown-fenced JSON

Then manually verify this state machine:
- employee request -> `Requested`
- question generation -> `Pending SME Review`
- reviewer selection -> `Approved`
- manager selects five -> `Assigned`
- employee submits responses -> `Completed` assignment plus `Scored` result
- manager calibration -> `Calibrated`
- calibration creates skill assessment and gap/TNI rows

Also verify that assignments use only approved-for-schedule questions, critical failures force `Fail`, and the dashboard includes application-created output rows.

Do not reset `Talent360i_Output.xlsx`. Report missing workbook tabs, unavailable API credentials, and unrelated legacy-module failures separately from issues introduced by the active pages.
```

## Optional Prompt: Improve The UI

```text
Improve the Streamlit UI without changing the workbook contract.

Keep the numbered page order and make each page show:
- a short purpose statement
- the current workflow status and source tab
- one primary action
- clear success and error messages

Do not put assessment questions on the Employee Request page. Keep assignment selection at five questions. Preserve workbook mappings and status values. Validate with a local run and workbook-backed smoke test.
```

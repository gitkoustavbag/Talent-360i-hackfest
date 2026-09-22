# Talent 360 Video Script


## Story in One Sentence

Talent 360 turns a role-mapped employee request into a governed assessment, an evidence-backed manager calibration, and a practical development action.

## Recording Order

The sidebar order is the workflow order. The app may display `6. Admin Question Bank` before `3. Reviewer Approval` in the sidebar, but the story is clearer when question generation is shown before approval and assignment.

---

## Scene 1: Opening and Challenge

**Time:** 0:00-0:40

**Screen:** Home page, `Talent 360`.

**Action:** Show the workflow journey cards. Briefly point to Employee Request, Question Supply, Reviewer Approval, Manager Assignment, Employee Assessment, Manager Review, and Talent Dashboard.

**Narration:**

> Talent 360 is a governed, AI-assisted capability assessment workflow. It starts with a focused employee request and carries that request through question generation, expert review, assessment, manager calibration, and development action. The goal is not just to produce a score. The goal is to create a trusted decision with evidence, human oversight, and a clear next step.
>
> This demo uses the provided workbook as the reference data layer and records workflow decisions and evidence in the output workbook.

**On-screen callout:** `Working workflow | Human approval | Evidence and audit trail`

---

## Scene 2: Employee Request

**Time:** 0:40-1:20

**Screen:** `1. Employee Request`.

**Action:**

1. Select the seeded employee.
2. Select a role-mapped skill.
3. Select the target proficiency level.
4. Show the employee context and the role/skill mapping.
5. Click the request submission button.
6. Pause on the success message and status.

**Narration:**

> I begin by selecting an employee, a skill that is mapped to the employee's role, and the target proficiency level. These choices keep the assessment relevant to the person's actual role instead of creating a generic questionnaire.
>
> When I submit the request, Talent 360 creates an `Assessment_Requests` record and logs the request event. The request is now the starting point for the governed workflow.

**Security and governance point:**

> The form is constrained by reference data. The app does not accept an arbitrary skill or level that is disconnected from the role model.

**Transition:**

> Next, the system needs a question supply that is specific to this role, skill, and target level.

---

## Scene 3: AI Question Supply

**Time:** 1:20-2:00

**Screen:** `6. Admin Question Bank`.

**Action:**

1. Select the role, blueprint, skill, and target level.
2. Show the generation settings and the expected Easy, Medium, and Hard distribution.
3. Click the generate button.
4. Show the generated questions and their initial status: `Pending SME Review`.
5. Point out that the questions are not immediately assignable.

**Narration:**

> The administrator can generate a role- and skill-specific question bank. The application requests ten multiple-choice questions with a balanced difficulty mix: three Easy, four Medium, and three Hard.
>
> The important control is what happens next. AI output is treated as a draft. Each question is parsed and validated, then saved as `Pending SME Review` with scheduling disabled. Generation alone never makes a question available to an employee.

**Security and responsible-AI point:**

> Credentials stay outside the code in environment configuration. Generated content is validated before it is stored, and a human subject-matter expert remains responsible for deciding whether a question is suitable for use.

**Fallback if live generation is unavailable:**

> If the AI service is unavailable during recording, use the seeded question bank and say: “This run uses the validated seeded question bank. The same SME gate applies to generated questions.” Do not display an API key or fabricate a successful generation result.

---

## Scene 4: SME Reviewer Approval

**Time:** 2:00-2:45

**Screen:** `3. Reviewer Approval`.

**Action:**

1. Enter a reviewer role, such as `SME Reviewer`.
2. Open a pending question.
3. Read the question and options briefly.
4. If appropriate, edit the wording to demonstrate review ownership.
5. Select `Approve` and save the decision.
6. Repeat until at least five suitable questions are approved, including Easy, Medium, and Hard coverage.
7. Show the resulting approved status and `Approved for schedule` state.

**Narration:**

> This is the human-in-the-loop gate. The reviewer can inspect the wording, edit it, approve it, reject it, or request a revision. The effective wording is the wording that is saved for use.
>
> Only questions with an approved SME status and an explicit `Approved for schedule` flag can move forward. Rejected questions are not silently returned to the active queue. This gives the team a clear quality decision and an audit trail for the question supply.

**Security and governance point:**

> This gate addresses unsafe or unsuitable generated content before it reaches an employee.

**Transition:**

> With approved coverage in place, the manager can now create a controlled assessment assignment.

---

## Scene 5: Manager Assignment

**Time:** 2:45-3:30

**Screen:** `2. Manager Assignment`.

**Action:**

1. Select the open employee request.
2. Select the role blueprint and available schedule.
3. Select exactly five approved questions.
4. Show that the selection includes at least one Easy, one Medium, and one Hard question.
5. Click the assignment action.
6. Pause on the success message and the new `Assigned` status.

**Narration:**

> The manager now turns the request into a ready assessment. The page uses the approved question bank, not the raw AI drafts, and requires a five-question assignment with Easy, Medium, and Hard coverage.
>
> Submitting the assignment writes the assignment and its question links to the output workbook, updates the request to `Assigned`, and preserves the selected schedule. The manager is choosing from governed content rather than bypassing review.

**On-screen callout:** `5 questions | Approved content only | Difficulty coverage`

---

## Scene 6: Employee Assessment and Scoring

**Time:** 3:30-4:30

**Screen:** `4. Employee Assessment`.

**Action:**

1. Select the employee and the incomplete assignment.
2. Answer each assigned question.
3. For a clean pass demonstration, choose the correct answers and submit.
4. Show the score, pass/fail result, recommended current level, and critical-failure indicator.
5. If demonstrating the failure path instead, answer one critical question incorrectly and show the automatic fail behavior. Do not create both paths unless the data is reset between takes.

**Narration:**

> The employee sees only the questions assigned to this assessment. On submission, each response is recorded and the application calculates the score percentage and recommended current level.
>
> The pass threshold is 75 percent. A critical question has an additional control: an incorrect answer sets the critical-failure flag and causes a failure even when the percentage would otherwise pass. The result is written as `Scored`, and the assignment is marked complete.

**Security and responsible-AI point:**

> The score is application-calculated from the stored answer key and policy rules. The AI does not make the final assessment decision, and the employee's raw answers are not sent to the dashboard summary.

**Transition:**

> A score is evidence, but it is not the final talent decision. That is where manager review and SME signoff enter.

---

## Scene 7: Manager Review and Calibration

**Time:** 4:30-5:25

**Screen:** `5. Manager Review`.

**Action:**

1. Select the scored result.
2. Show the objective recommendation and score.
3. Enter or select a calibrated proficiency level.
4. Demonstrate the evidence validation and SME signoff controls.
5. Confirm the review.
6. Show the calibrated status, final level, skill gap, and training recommendation.

**Narration:**

> The manager reviews the scored result alongside the available evidence. Calibration is not open-ended: the final level is bounded to no more than one level above or below the objective recommendation.
>
> The manager must validate the evidence and record SME signoff before the result can be finalized. Once confirmed, Talent 360 writes the calibrated skill assessment and creates a training or development recommendation from the target level, current level, and training map.
>
> If the result is a fail, the manager can send it back for reassessment. The original result remains preserved for audit, reassessment is limited to two attempts, and the next due date is refreshed by 30 days.

**On-screen callout:** `Objective score -> Evidence -> SME signoff -> Bounded calibration -> Development action`

---

## Scene 8: Dashboard and AI Decision Brief

**Time:** 5:25-6:20

**Screen:** `7. Dashboard`.

**Action:**

1. Show the metric row: assessments, average score, pass rate, calibrated results, and high gaps.
2. Scroll through outcome and capability analysis.
3. Show the gap and training recommendation area.
4. Show the AI decision brief and its evidence-grounded label.
5. Expand detailed result or gap records if useful.

**Narration:**

> The dashboard turns individual assessment records into a portfolio view. It shows assessment volume, average score, pass rate, calibration activity, and high gaps.
>
> The gap view connects the current level to the target level and surfaces mapped training actions. The optional AI decision brief summarizes aggregated scores, outcomes, gaps, and course signals to suggest practical next actions.
>
> The privacy boundary is explicit: the brief uses aggregated signals and does not send raw employee answers. The dashboard supports a decision; it does not replace manager accountability.

**On-screen callout:** `Evidence-led insight | Aggregated signals | Actionable development`

---

## Scene 9: Architecture and Data Map

**Time:** 6:20-7:20

**Screen:** `8. Architecture`, then `9. Data Map`.

**Action:**

1. On Architecture, trace the flow from request to development action.
2. Point to the governance points before and after assessment.
3. On Data Map, show the input and output workbook roles.
4. Show the input tabs and output tabs without exposing sensitive values.
5. Point out the audit log and workflow hand-offs.

**Narration:**

> The architecture view shows where controls are applied: role mapping at intake, validation and SME approval before assignment, scoring and critical-failure policy during assessment, and evidence plus signoff before calibration.
>
> The data map separates the read-only reference workbook from the writable output workbook. Reference tabs define users, roles, skills, levels, blueprints, schedules, questions, and training mappings. Output tabs preserve requests, assignments, responses, results, SME decisions, skill assessments, gaps, and audit events.
>
> That separation makes the workflow explainable and keeps the evidence of each decision available for review.

---

## Scene 10: Closing

**Time:** 7:20-7:50

**Screen:** Return to Dashboard or Home page.

**Narration:**

> The current demo uses a local workbook persistence layer and seeded data; production deployment would add authenticated role-based access, transactional persistence, privacy controls, and hardened model-output handling.

> Talent 360 connects capability measurement to action without removing people from the decision. It combines role-mapped data, validated question supply, SME approval, policy-based scoring, manager calibration, and mapped development recommendations.
>
> The result is a repeatable workflow that is secure by design, responsible in its use of AI, and ready to move from prototype evidence toward real talent operations.

**Final on-screen message:**

`Talent 360: from capability signal to governed growth action.`

---

## Claims to Make Carefully

- Say “AI-assisted” or “AI-generated drafts,” not “fully autonomous assessment.”
- Say “the application calculates the score,” not “the AI decides the score.”
- Say “optional AI decision brief based on aggregated signals,” not “AI reads employee answers.”
- Explain that SME approval is required before questions are assignable.
- Mention the 75% pass threshold, critical-question auto-fail policy, bounded calibration, audit records, and reassessment limit only when those behaviors are visible in the current build.
- Do not claim external identity, encryption, or production compliance unless those controls are demonstrated separately. The video should show the implemented application controls and describe deployment controls as future production requirements.

## Short Backup Version

If recording time is limited, use this 3-minute sequence:

1. Home page: explain the problem and the end-to-end journey.
2. Employee Request: create a role-mapped request.
3. Reviewer Approval: show the human approval gate.
4. Manager Assignment: select five approved questions with difficulty coverage.
5. Employee Assessment: submit answers and show policy-based scoring.
6. Manager Review: show evidence, signoff, calibration, and development action.
7. Dashboard: show portfolio metrics, gaps, training, and the privacy note.
8. Architecture/Data Map: close with the workbook and audit story.

Use the full narration from Scenes 1, 4, 5, 6, 7, and 8, compressing each to one or two sentences.

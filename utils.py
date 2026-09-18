# utils.py
import json
import re


def _catalog_values(sheet_name, columns):
    """Read unique catalog values from the workbook, preserving Excel order."""
    try:
        from db import load_sheet

        frame = load_sheet(sheet_name)
        for column in columns:
            if column in frame.columns:
                values = frame[column].dropna().astype(str).str.strip()
                values = [value for value in values.tolist() if value]
                if values:
                    return list(dict.fromkeys(values))
    except Exception:
        pass
    return []


def _derived_catalog_values(sheet_columns):
    """Derive catalog values from the existing question and assessment sheets."""
    values = []
    try:
        from db import load_sheet

        for sheet_name, column in sheet_columns:
            frame = load_sheet(sheet_name)
            if column in frame.columns:
                values.extend(frame[column].dropna().astype(str).str.strip().tolist())
    except Exception:
        return []
    return list(dict.fromkeys(value for value in values if value))


SKILLS = _catalog_values("skills", ("skill", "name"))
if not SKILLS:
    SKILLS = _derived_catalog_values((("questions", "skill"), ("assessments", "skill")))
if not SKILLS:
    SKILLS = ["AI", "REST API Design", "Python", "Data Analysis"]

LEVELS = _catalog_values("levels", ("level", "name"))
if not LEVELS:
    LEVELS = _derived_catalog_values(
        (("questions", "level"), ("assessments", "requested_level"))
    )
if not LEVELS:
    LEVELS = ["Beginner", "Intermediate", "Advanced"]

def parse_questions(data):
    """Parse JSON or Markdown-fenced JSON into a list of questions."""
    if isinstance(data, str):
        # Remove markdown fences
        fenced = re.sub(r"```json|```", "", data).strip()
        parsed = json.loads(fenced)
        if "questions" in parsed:
            parsed = parsed["questions"]
        data = parsed
    if isinstance(data, dict):
        data = [data]
    if isinstance(data, list):
        normalized = []
        for question in data:
            question = dict(question)
            if question.get("answer") is None:
                question["answer"] = question.get("correct_answer", question.get("correctAnswer"))
            answer = question.get("answer")
            options = question.get("options", [])
            if isinstance(answer, int) and 0 <= answer < len(options):
                question["answer"] = options[answer]
            elif isinstance(answer, str) and answer.isdigit():
                answer_index = int(answer)
                if 0 <= answer_index < len(options):
                    question["answer"] = options[answer_index]
            normalized.append(question)
        return normalized
    raise ValueError("Unsupported question format")

def validate_question(q):
    """Validate a single question dict."""
    if not q.get("id") or not q.get("question"):
        raise ValueError("Missing id or question text")
    if len(q.get("options", [])) != 4:
        raise ValueError("Must have exactly 4 options")
    if q.get("answer") is None:
        raise ValueError("Missing answer")
    return True


def answer_to_option(answer, options):
    """Convert a generated answer into the workbook's A-D option format."""
    if len(options) != 4:
        raise ValueError("Must have exactly 4 options")

    answer_text = str(answer).strip()
    normalized = answer_text.upper().rstrip(".")
    labels = {"A": 0, "B": 1, "C": 2, "D": 3}
    if normalized in labels:
        return normalized

    if normalized.startswith("OPTION ") and normalized[-1:] in labels:
        return normalized[-1]

    option_values = [str(option).strip() for option in options]
    if answer_text in option_values:
        return "ABCD"[option_values.index(answer_text)]

    raise ValueError(
        f"Answer {answer_text!r} must be A-D or match one of the four options"
    )

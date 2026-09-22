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
    """Validate a generated question before it enters the question bank."""
    question_id = str(q.get("id", "")).strip()
    question_text = str(q.get("question", "")).strip()
    options = q.get("options")
    answer = q.get("answer")
    difficulty = str(q.get("difficulty", "")).strip().lower()

    if not question_id or not question_text:
        raise ValueError("Missing id or question text")
    if len(question_id) > 120 or len(question_text) > 2000:
        raise ValueError("Question id or text is too long")
    if not isinstance(options, list) or len(options) != 4:
        raise ValueError("Must have exactly 4 options")
    normalized_options = [str(option).strip() for option in options]
    if any(not option or len(option) > 1000 for option in normalized_options):
        raise ValueError("Each option must be non-empty and no longer than 1000 characters")
    if len(set(option.casefold() for option in normalized_options)) != 4:
        raise ValueError("Options must be unique")
    if answer is None:
        raise ValueError("Missing answer")
    if difficulty and difficulty not in {"easy", "medium", "hard"}:
        raise ValueError("Difficulty must be Easy, Medium, or Hard")
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


def normalize_difficulty(value, index=None, total=None):
    """Return a valid Easy/Medium/Hard label without confusing target level with difficulty."""
    normalized = str(value).strip().lower() if value is not None else ""
    if normalized in {"easy", "medium", "hard"}:
        return normalized.title()

    if index is not None and total:
        easy_end = max(1, round(total * 0.3))
        medium_end = easy_end + max(1, round(total * 0.4))
        if index < easy_end:
            return "Easy"
        if index < medium_end:
            return "Medium"
        return "Hard"

    return "Unclassified"

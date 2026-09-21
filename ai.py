import json
import os

import pandas as pd
from dotenv import load_dotenv

load_dotenv()

PROVIDER = os.getenv("PROVIDER", "openai").lower()

# =====================================================
# OPENAI CONFIG
# =====================================================
if PROVIDER == "openai":
    import openai

    MODEL = os.getenv("OPENAI_MODEL", "gpt-4")

# =====================================================
# AZURE CONFIG
# =====================================================
elif PROVIDER == "azure":
    from azure.ai.inference import ChatCompletionsClient
    from azure.core.credentials import AzureKeyCredential

    MODEL = os.getenv(
        "AZURE_MODEL",
        "hack-fest-gpt-5.6-luna"
    )

else:
    raise ValueError(
        f"Unsupported PROVIDER: {PROVIDER}"
    )


client = None


def get_client():
    """Create the configured AI client only when question generation is requested."""
    global client
    if client is not None:
        return client

    if PROVIDER == "openai":
        api_key = os.getenv("OPENAI_API_KEY", "").strip()
        if not api_key:
            raise RuntimeError(
                "OPENAI_API_KEY is not configured. Add it to .env, then restart Streamlit."
            )
        client = openai.OpenAI(api_key=api_key)
    else:
        endpoint = os.getenv("AZURE_ENDPOINT", "").strip()
        api_key = os.getenv("AZURE_API_KEY", "").strip()
        if not endpoint or not api_key:
            raise RuntimeError(
                "AZURE_ENDPOINT and AZURE_API_KEY are not configured. Add them to .env, "
                "then restart Streamlit."
            )
        client = ChatCompletionsClient(
            endpoint=endpoint,
            credential=AzureKeyCredential(api_key),
            api_version="2025-03-01-preview",
        )
    return client


def generate_questions(skill, level, count=10):

    prompt = f"""
Generate {count} multiple choice questions for skill '{skill}'
at level '{level}'. For a 10-question bank, use this difficulty mix:
3 Easy, 4 Medium, and 3 Hard. For other counts, keep the distribution
as balanced as possible across Easy, Medium, and Hard.

Each question must contain:
- id
- question
- 4 options
- answer
- difficulty
- rationale

Return ONLY JSON array.
"""

    # ==========================================
    # OPENAI
    # ==========================================
    if PROVIDER == "openai":

        response = get_client().chat.completions.create(
            model=MODEL,
            messages=[
                {
                    "role": "system",
                    "content":
                    "You are an AI question generator."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.7
        )

        return response.choices[0].message.content

    # ==========================================
    # AZURE
    # ==========================================
    else:

        response = get_client().complete(
            model=MODEL,
            messages=[
                {
                    "role": "system",
                    "content":
                    "You are an AI question generator."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        return response.choices[0].message.content


def build_dashboard_summary_payload(results, gaps, calibrated_count, average_score, pass_count, fail_count, high_gap_count):
    """Build a dashboard summary payload rich enough for an evidence-based talent recommendation summary."""
    gap_counts = (
        gaps["skill"].value_counts().head(5).to_dict()
        if isinstance(gaps, pd.DataFrame) and "skill" in gaps.columns
        else {}
    )

    course_values = []
    training_recommendations = []
    if isinstance(gaps, pd.DataFrame) and not gaps.empty:
        course_values = (
            gaps["recommended_course_id"]
            .dropna()
            .astype(str)
            .replace("", pd.NA)
            .dropna()
            .unique()
            .tolist()
        )

        relevant_columns = [col for col in ["user_id", "skill", "recommended_course_id", "gap_severity", "tni_recommendation"] if col in gaps.columns]
        if "recommended_course_id" in gaps.columns and relevant_columns:
            training_frame = gaps[relevant_columns].dropna(subset=["recommended_course_id"]).copy()
            training_recommendations = [
                {
                    "user_id": str(row.get("user_id", "Unknown")).strip() or "Unknown",
                    "skill": str(row.get("skill", "Unknown")).strip() or "Unknown",
                    "recommended_course_id": str(row.get("recommended_course_id", "")).strip(),
                    "gap_severity": str(row.get("gap_severity", "")).strip(),
                    "tni_recommendation": str(row.get("tni_recommendation", "")).strip() if "tni_recommendation" in row else "",
                }
                for _, row in training_frame.iterrows()
            ]

    return {
        "assessment_count": len(results) if isinstance(results, pd.DataFrame) else 0,
        "scored_count": int((results.get("result_status", pd.Series(dtype=str)) == "Scored").sum()) if isinstance(results, pd.DataFrame) else 0,
        "calibrated_count": calibrated_count,
        "average_score_pct": average_score,
        "pass_count": pass_count,
        "fail_count": fail_count,
        "critical_fail_count": int((results.get("critical_fail_flag", pd.Series(dtype=str)) == "Yes").sum()) if isinstance(results, pd.DataFrame) and "critical_fail_flag" in results.columns else 0,
        "gap_counts_by_skill": gap_counts,
        "high_gap_count": high_gap_count,
        "recommended_courses": course_values[:10],
        "training_recommendations": training_recommendations[:25],
    }


def format_dashboard_summary_html(summary_text):
    """Convert a text summary into structured HTML that is readable in the dashboard."""
    if not summary_text:
        return "<p>No summary available.</p>"

    lines = str(summary_text).replace("\r\n", "\n").split("\n")
    html = []
    in_list = False

    def close_list():
        nonlocal in_list
        if in_list:
            html.append("</ul>")
            in_list = False

    for raw_line in lines:
        line = raw_line.strip()
        if not line:
            close_list()
            continue

        lowered = line.lower()
        if lowered.startswith("executive summary"):
            close_list()
            html.append("<h3 class='ai-summary-section'>Executive summary</h3>")
            continue
        if lowered.startswith("key signals"):
            close_list()
            html.append("<h3 class='ai-summary-section'>Key signals</h3>")
            continue
        if lowered.startswith("recommended actions"):
            close_list()
            html.append("<h3 class='ai-summary-section'>Recommended actions</h3>")
            continue
        if lowered.startswith("course catalogue"):
            close_list()
            html.append("<h3 class='ai-summary-section'>Course catalogue</h3>")
            continue

        if line.startswith(("- ", "* ")):
            if not in_list:
                html.append("<ul class='ai-summary-list'>")
                in_list = True
            html.append(f"<li>{line[2:].strip()}</li>")
            continue

        if line.startswith(tuple(f"{i}. " for i in range(1, 10))):
            if not in_list:
                html.append("<ul class='ai-summary-list'>")
                in_list = True
            html.append(f"<li>{line.split('. ', 1)[1].strip()}</li>")
            continue

        if ":" in line and len(line.split(":", 1)[0].strip()) <= 40:
            key, value = line.split(":", 1)
            close_list()
            html.append(
                f"<div class='ai-summary-card'><div class='ai-summary-key'>{key.strip()}</div><div class='ai-summary-value'>{value.strip()}</div></div>"
            )
            continue

        close_list()
        html.append(f"<p>{line}</p>")

    close_list()
    return "\n".join(html)


def summarize_dashboard(summary):
    """Generate a concise leadership summary from aggregated dashboard metrics."""
    prompt = f"""
You are a talent analytics advisor. Summarize these aggregated assessment metrics:
{json.dumps(summary, default=str)}

Return a concise but structured markdown summary with exactly these section headings in this order:
Executive summary
Key signals
Recommended actions
Course catalogue

Formatting rules:
- Use short, evidence-based bullets under each section.
- In Recommended actions, create employee-level actions in the format:
  Employee: <user_id> | Skill gap: <skill> | Course: <course_id> | Rationale: <short reason>
- In Course catalogue, list the shared training courses as separate bullets with a short reason for relevance.
- Keep the summary readable, concise, and grounded in the data only.
- Mention when the sample is small or data is incomplete.
- Do not invent names, course content, or scores that are not in the source data.
"""
    messages = [
        {
            "role": "system",
            "content": "You provide evidence-grounded talent analytics summaries.",
        },
        {"role": "user", "content": prompt},
    ]
    if PROVIDER == "openai":
        response = get_client().chat.completions.create(
            model=MODEL,
            messages=messages,
            temperature=0.2,
        )
    else:
        response = get_client().complete(model=MODEL, messages=messages)
    return response.choices[0].message.content
import json
import os
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


def summarize_dashboard(summary):
    """Generate a concise leadership summary from aggregated dashboard metrics."""
    prompt = f"""
You are a talent analytics advisor. Summarize these aggregated assessment metrics:
{json.dumps(summary, default=str)}

Return a concise plain-text summary with exactly these sections:
Executive summary
Key signals
Recommended actions

Do not invent facts, names, scores, or causes that are not present in the data.
Mention when the sample is small or data is incomplete.
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
import os
from dotenv import load_dotenv

load_dotenv()

PROVIDER = os.getenv("PROVIDER", "openai").lower()

# =====================================================
# OPENAI CONFIG
# =====================================================
if PROVIDER == "openai":
    import openai

    client = openai.OpenAI(
        api_key=os.getenv("OPENAI_API_KEY")
    )

    MODEL = os.getenv("OPENAI_MODEL", "gpt-4")

# =====================================================
# AZURE CONFIG
# =====================================================
elif PROVIDER == "azure":
    from azure.ai.inference import ChatCompletionsClient
    from azure.core.credentials import AzureKeyCredential

    client = ChatCompletionsClient(
        endpoint=os.getenv("AZURE_ENDPOINT"),
        credential=AzureKeyCredential(
            os.getenv("AZURE_API_KEY")
        ),
        api_version="2025-03-01-preview"
    )

    MODEL = os.getenv(
        "AZURE_MODEL",
        "hack-fest-gpt-5.6-luna"
    )

else:
    raise ValueError(
        f"Unsupported PROVIDER: {PROVIDER}"
    )


def generate_questions(skill, level, count=10):

    prompt = f"""
Generate {count} multiple choice questions for skill '{skill}'
at level '{level}'.

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

        response = client.chat.completions.create(
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

        response = client.complete(
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
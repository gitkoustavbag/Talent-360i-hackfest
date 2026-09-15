# ai.py
import os
import openai
from dotenv import load_dotenv

load_dotenv()
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

MODEL = "gpt-4"
PROMPT_VERSION = "v2"

def generate_questions(skill, level, count=10):
    """Generate MCQs using OpenAI."""
    prompt = f"""
    Generate {count} multiple-choice questions for skill '{skill}' at level '{level}'.
    Each question must have:
    - id
    - question
    - 4 options
    - answer: the exact text of one item in options
    - difficulty
    - rationale
    Return only a JSON array. Do not use markdown fences or extra commentary.
    """
    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "system", "content": "You are an AI question generator."},
                  {"role": "user", "content": prompt}],
        temperature=0.7
    )
    return response.choices[0].message.content

import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    raise RuntimeError("GEMINI_API_KEY missing")

client = genai.Client(api_key=API_KEY)

MODEL = "models/gemini-2.0-flash"


def generate_text(prompt: str) -> str:
    resp = client.models.generate_content(
        model=MODEL,
        contents=prompt,
        config={
            "temperature": 0.2,
            "max_output_tokens": 700,
        },
    )
    return (resp.text or "").strip()

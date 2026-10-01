import os
from functools import lru_cache

from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

DEFAULT_MODEL = DEFAULT_MODEL = "gemini-3.5-flash-lite"


@lru_cache(maxsize=1)
def get_client():
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise RuntimeError(
            "GEMINI_API_KEY is not set in the .env file."
        )

    return genai.Client(api_key=api_key)


def generate_text(
    prompt: str,
    temperature: float = 0.7,
    max_output_tokens: int = 1000,
) -> str:

    client = get_client()

    response = client.models.generate_content(
        model=DEFAULT_MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(
            temperature=temperature,
            max_output_tokens=max_output_tokens,
        ),
    )

    if response.text:
        return response.text.strip()

    return ""
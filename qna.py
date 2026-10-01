from gemini_client import generate_text


def answer_question(question: str) -> str:
    prompt = f"""
You are EduGenie, a student-friendly educational assistant.

Answer the student's question accurately and concisely.

Use simple language.

If the question contains a difficult concept,
explain it briefly.

If the question is ambiguous,
state the assumption you are making.

Do not invent citations or sources.

Student question:

{question}
"""

    return generate_text(
        prompt,
        temperature=0.3
    )
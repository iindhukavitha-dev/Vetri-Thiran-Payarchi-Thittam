from gemini_client import generate_text


def get_learning_recommendations(topic: str) -> list:
    prompt = f"""
Create a simple learning path for a college student studying {topic}.

Give:
1. Basic concepts
2. Important concepts
3. Practice topics
4. Advanced concepts
5. A small project idea
"""

    try:
        result = generate_text(prompt)

        if result:
            return [
                {
                    "topic": topic,
                    "recommendations": result
                }
            ]

    except Exception:
        pass

    return [
        {
            "topic": topic,
            "recommendations": [
                f"Learn the basics of {topic}",
                f"Study important concepts in {topic}",
                f"Practice {topic} with examples",
                f"Work on advanced {topic} concepts",
                f"Build a small project using {topic}"
            ]
        }
    ]

import json
from typing import Any, Optional

from app.config import settings
from app.service.fallback import (
    home_fallback,
    jewelry_fallback,
    party_fallback,
)


def _clean_json_text(text: str) -> str:
    text = text.strip()

    if text.startswith("```"):
        lines = text.splitlines()

        if lines:
            lines = lines[1:]

        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]

        text = "\n".join(lines)

    return text.strip()


def _validate_ai_response(
    data: dict[str, Any],
    planner_type: str,
    budget: float,
) -> dict[str, Any]:

    data["planner_type"] = planner_type
    data["budget"] = float(budget)

    data.setdefault("allocations", {})
    data.setdefault("recommendations", [])
    data.setdefault("summary", "AI recommendations generated.")

    total = 0.0

    cleaned_items = []

    for item in data.get("recommendations", []):
        try:
            price = float(
                item.get(
                    "estimated_price",
                    0,
                )
            )
        except (TypeError, ValueError):
            price = 0.0

        quantity = int(
            item.get(
                "quantity",
                1,
            ) or 1
        )

        total += price

        cleaned_items.append(
            {
                "category": str(
                    item.get(
                        "category",
                        "General",
                    )
                ),
                "name": str(
                    item.get(
                        "name",
                        "Recommended item",
                    )
                ),
                "platform": str(
                    item.get(
                        "platform",
                        "Amazon",
                    )
                ),
                "estimated_price": round(
                    max(price, 0),
                    2,
                ),
                "quantity": max(
                    quantity,
                    1,
                ),
                "reason": str(
                    item.get(
                        "reason",
                        "Matches the requested requirements.",
                    )
                ),
                "search_url": item.get(
                    "search_url"
                ),
            }
        )

    # Prevent accidental over-budget AI results.
    if total > budget and cleaned_items:
        scale = budget / total

        for item in cleaned_items:
            item["estimated_price"] = round(
                item["estimated_price"] * scale,
                2,
            )

        total = sum(
            item["estimated_price"]
            for item in cleaned_items
        )

    data["recommendations"] = cleaned_items
    data["total_estimated"] = round(
        min(total, budget),
        2,
    )

    data["remaining_budget"] = round(
        max(
            budget - data["total_estimated"],
            0,
        ),
        2,
    )

    data["ai_powered"] = True

    return data


def _generate_with_gemini(
    prompt: str,
    image_bytes: Optional[bytes] = None,
    mime_type: Optional[str] = None,
) -> Optional[dict[str, Any]]:

    if not settings.gemini_api_key:
        return None

    try:
        from google import genai
        from google.genai import types

        client = genai.Client(
            api_key=settings.gemini_api_key
        )

        contents: list[Any] = [prompt]

        if image_bytes:
            contents.append(
                types.Part.from_bytes(
                    data=image_bytes,
                    mime_type=mime_type or "image/jpeg",
                )
            )

        response = client.models.generate_content(
            model=settings.gemini_model,
            contents=contents,
            config=types.GenerateContentConfig(
                temperature=0.4,
                response_mime_type="application/json",
            ),
        )

        text = getattr(
            response,
            "text",
            None,
        )

        if not text:
            return None

        return json.loads(
            _clean_json_text(text)
        )

    except Exception:
        return None


def generate_home_recommendations(
    budget: float,
    rooms: list[str],
    style: str,
    notes: str = "",
) -> dict[str, Any]:

    prompt = f"""
You are PocketSmart AI, a budget-aware home interior recommendation assistant.

User budget: {budget}
Rooms: {rooms}
Preferred style: {style}
Additional notes: {notes}

Create practical recommendations for furniture, lighting, decor,
and utilities.

Return ONLY valid JSON using this structure:

{{
  "summary": "short summary",
  "allocations": {{
    "Furniture": 0,
    "Lighting": 0,
    "Decor": 0,
    "Utilities": 0,
    "Reserve": 0
  }},
  "recommendations": [
    {{
      "category": "Furniture",
      "name": "item name",
      "platform": "Amazon",
      "estimated_price": 0,
      "quantity": 1,
      "reason": "reason",
      "search_url": null
    }}
  ]
}}

Never exceed the supplied budget.
Use platforms such as Amazon, Flipkart and IKEA.
"""

    result = _generate_with_gemini(prompt)

    if result:
        return _validate_ai_response(
            result,
            "home",
            budget,
        )

    return home_fallback(
        budget=budget,
        rooms=rooms,
        style=style,
        notes=notes,
    )


def generate_party_recommendations(
    budget: float,
    guests: int,
    event_type: str,
    venue: str = "",
    preferences: str = "",
) -> dict[str, Any]:

    prompt = f"""
You are PocketSmart AI, a party budget planning assistant.

Budget: {budget}
Guests: {guests}
Event type: {event_type}
Venue: {venue}
Preferences: {preferences}

Allocate the budget across catering, decoration,
entertainment and venue.

Use platforms such as Swiggy, Zomato, OYO and Amazon.

Return ONLY valid JSON:

{{
  "summary": "short summary",
  "allocations": {{
    "Catering": 0,
    "Decoration": 0,
    "Entertainment": 0,
    "Venue": 0,
    "Reserve": 0
  }},
  "recommendations": [
    {{
      "category": "Catering",
      "name": "item",
      "platform": "Swiggy",
      "estimated_price": 0,
      "quantity": 1,
      "reason": "reason",
      "search_url": null
    }}
  ]
}}

Never exceed the supplied budget.
"""

    result = _generate_with_gemini(prompt)

    if result:
        return _validate_ai_response(
            result,
            "party",
            budget,
        )

    return party_fallback(
        budget=budget,
        guests=guests,
        event_type=event_type,
        venue=venue,
        preferences=preferences,
    )


def generate_jewelry_recommendations(
    budget: float,
    occasion: str,
    outfit_description: str,
    image_bytes: Optional[bytes] = None,
    mime_type: Optional[str] = None,
) -> dict[str, Any]:

    prompt = f"""
You are PocketSmart AI, a jewelry recommendation assistant.

Budget: {budget}
Occasion: {occasion}
Outfit description: {outfit_description}

If an outfit image is provided, analyze its broad visual characteristics
such as colors, style, formality and patterns.

Recommend coordinated earrings, necklace and bracelet options.

Return ONLY valid JSON:

{{
  "summary": "short summary",
  "allocations": {{
    "Earrings": 0,
    "Necklace": 0,
    "Bracelet": 0,
    "Reserve": 0
  }},
  "recommendations": [
    {{
      "category": "Earrings",
      "name": "item",
      "platform": "Amazon",
      "estimated_price": 0,
      "quantity": 1,
      "reason": "reason",
      "search_url": null
    }}
  ]
}}

Never exceed the supplied budget.
"""

    result = _generate_with_gemini(
        prompt,
        image_bytes=image_bytes,
        mime_type=mime_type,
    )

    if result:
        return _validate_ai_response(
            result,
            "jewelry",
            budget,
        )

    return jewelry_fallback(
        budget=budget,
        occasion=occasion,
        outfit_description=outfit_description,
        image_provided=image_bytes is not None,
    )
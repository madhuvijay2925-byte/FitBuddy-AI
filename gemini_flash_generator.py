import os

from dotenv import load_dotenv
from google import genai


load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY", "").strip()

MODEL = os.getenv(
    "GEMINI_TIP_MODEL",
    "gemini-2.5-flash"
)

ALLOW_DEMO_FALLBACK = (
    os.getenv("ALLOW_DEMO_FALLBACK", "true").lower()
    == "true"
)


def demo_tip(goal):

    goal = goal.lower()

    if "muscle" in goal:
        return (
            "Include protein-rich foods, enough calories, "
            "vegetables, whole grains and adequate water. "
            "Recovery and sleep are also important."
        )

    if "weight" in goal:
        return (
            "Focus on balanced meals with vegetables, "
            "protein, whole grains and adequate water. "
            "Avoid relying on extreme diets."
        )

    return (
        "Eat balanced meals containing protein, vegetables, "
        "whole grains and healthy fats. Stay hydrated and "
        "prioritize regular sleep."
    )


def generate_nutrition_tip_with_flash(goal):

    if not API_KEY:

        if ALLOW_DEMO_FALLBACK:
            return demo_tip(goal)

        raise RuntimeError(
            "GEMINI_API_KEY is missing."
        )

    prompt = f"""
Give one short practical nutrition and recovery tip
for a fitness user whose goal is:

{goal}

Keep it below 80 words.
Do not diagnose or treat medical conditions.
"""

    try:

        client = genai.Client(api_key=API_KEY)

        response = client.models.generate_content(
            model=MODEL,
            contents=prompt
        )

        return response.text

    except Exception as error:

        if ALLOW_DEMO_FALLBACK:
            return demo_tip(goal)

        raise RuntimeError(
            f"Gemini error: {error}"
        )
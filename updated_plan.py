import os

from dotenv import load_dotenv
from google import genai


load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY", "").strip()

MODEL = os.getenv(
    "GEMINI_WORKOUT_MODEL",
    "gemini-2.5-flash"
)

ALLOW_DEMO_FALLBACK = (
    os.getenv("ALLOW_DEMO_FALLBACK", "true").lower()
    == "true"
)


def demo_updated_plan(
    original_plan,
    feedback
):

    return f"""
UPDATED FITBUDDY PLAN

Previous Plan:
{original_plan}

User Feedback:
{feedback}

Updated Plan:

Day 1:
Light full-body workout.

Day 2:
Moderate cardio and stretching.

Day 3:
Upper-body strength exercises.

Day 4:
Recovery and mobility.

Day 5:
Lower-body strength exercises.

Day 6:
Cardio and core workout.

Day 7:
Rest and recovery.

The plan has been adjusted according
to the submitted feedback.
"""


def update_workout_plan(
    original_plan,
    feedback
):

    if not API_KEY:

        if ALLOW_DEMO_FALLBACK:
            return demo_updated_plan(
                original_plan,
                feedback
            )

        raise RuntimeError(
            "GEMINI_API_KEY is missing."
        )

    prompt = f"""
You are updating a 7-day fitness plan.

Original plan:
{original_plan}

User feedback:
{feedback}

Create a COMPLETE revised 7-day plan.

Keep the plan practical.
Clearly show Day 1 through Day 7.
Adjust the plan according to the feedback.
Do not diagnose medical conditions.
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
            return demo_updated_plan(
                original_plan,
                feedback
            )

        raise RuntimeError(
            f"Gemini error: {error}"
        )
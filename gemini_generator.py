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


def demo_workout_plan(
    username,
    age,
    weight,
    goal,
    intensity
):
    return f"""
FITBUDDY – 7 DAY WORKOUT PLAN

User: {username}
Age: {age}
Weight: {weight} kg
Goal: {goal}
Intensity: {intensity}

Day 1:
Full Body Strength
- Squats – 3 x 12
- Push-ups – 3 x 10
- Lunges – 3 x 10
- Plank – 3 x 30 sec

Day 2:
Cardio
- Brisk walking – 30 minutes
- Light stretching – 10 minutes

Day 3:
Upper Body
- Push-ups – 3 x 10
- Shoulder taps – 3 x 12
- Plank – 3 x 30 sec

Day 4:
Recovery
- Light walking – 20 minutes
- Stretching – 15 minutes

Day 5:
Lower Body
- Squats – 3 x 12
- Lunges – 3 x 10
- Glute bridge – 3 x 15

Day 6:
Cardio + Core
- Walking – 30 minutes
- Crunches – 3 x 12
- Plank – 3 x 30 sec

Day 7:
Rest and Recovery
- Gentle stretching
- Relaxation

Safety:
Start gradually and stop if you experience pain,
dizziness, or unusual symptoms.
"""


def generate_workout_gemini(
    username,
    age,
    weight,
    goal,
    intensity
):

    if not API_KEY:
        if ALLOW_DEMO_FALLBACK:
            return demo_workout_plan(
                username,
                age,
                weight,
                goal,
                intensity
            )

        raise RuntimeError(
            "GEMINI_API_KEY is missing."
        )

    prompt = f"""
Create a practical 7-day fitness workout plan.

User:
Name: {username}
Age: {age}
Weight: {weight} kg
Goal: {goal}
Intensity: {intensity}

Include:
- Day 1 to Day 7
- Exercises
- Sets/repetitions or duration
- Rest/recovery
- Safety note

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
            return demo_workout_plan(
                username,
                age,
                weight,
                goal,
                intensity
            )

        raise RuntimeError(
            f"Gemini error: {error}"
        )
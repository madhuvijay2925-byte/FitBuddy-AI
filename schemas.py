from typing import Literal

from pydantic import BaseModel, Field, field_validator


class UserInput(BaseModel):

    username: str = Field(
        min_length=2,
        max_length=120
    )

    user_id: str = Field(
        min_length=1,
        max_length=100
    )

    age: int = Field(
        ge=13,
        le=100
    )

    weight: float = Field(
        gt=20,
        le=400
    )

    goal: str = Field(
        min_length=2,
        max_length=100
    )

    intensity: Literal[
        "low",
        "medium",
        "high"
    ]

    @field_validator(
        "username",
        "user_id",
        "goal"
    )
    @classmethod
    def clean_text(cls, value):

        value = value.strip()

        if not value:
            raise ValueError(
                "This field cannot be empty."
            )

        return value


class FeedbackRequest(BaseModel):

    user_id: str = Field(
        min_length=1,
        max_length=100
    )

    feedback: str = Field(
        min_length=3,
        max_length=2000
    )


class WorkoutResponse(BaseModel):

    user_id: str

    username: str

    goal: str

    intensity: str

    workout_plan: str

    nutrition_tip: str


class FeedbackResponse(BaseModel):

    user_id: str

    updated_plan: str

    nutrition_tip: str
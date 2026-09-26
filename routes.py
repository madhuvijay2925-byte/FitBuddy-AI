from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates

from .database import (
    init_db,
    save_user,
    save_plan,
    get_user,
    get_plan,
    update_plan,
    get_all_users,
    delete_user
)

from .schemas import UserInput, FeedbackRequest

from .gemini_generator import generate_workout_gemini
from .gemini_flash_generator import (
    generate_nutrition_tip_with_flash
)
from .updated_plan import update_workout_plan


router = APIRouter()

templates = Jinja2Templates(
    directory="templates"
)

init_db()


@router.get("/", response_class=HTMLResponse)
def home(request: Request):

    return templates.TemplateResponse(
        "index.html",
        {"request": request}
    )


@router.get("/planner", response_class=HTMLResponse)
def planner(request: Request):

    return templates.TemplateResponse(
        "planner.html",
        {"request": request}
    )


@router.get("/nutrition", response_class=HTMLResponse)
def nutrition(request: Request):

    return templates.TemplateResponse(
        "nutrition.html",
        {"request": request}
    )


@router.get("/feedback", response_class=HTMLResponse)
def feedback(request: Request):

    return templates.TemplateResponse(
        "feedback.html",
        {"request": request}
    )


@router.post(
    "/generate-workout",
    response_class=HTMLResponse
)
def generate_workout(
    request: Request,
    username: str = Form(...),
    user_id: str = Form(...),
    age: int = Form(...),
    weight: float = Form(...),
    goal: str = Form(...),
    intensity: str = Form(...)
):

    try:

        user_data = UserInput(
            username=username,
            user_id=user_id,
            age=age,
            weight=weight,
            goal=goal,
            intensity=intensity
        )

        save_user(
            user_data.user_id,
            user_data.username,
            user_data.age,
            user_data.weight,
            user_data.goal,
            user_data.intensity
        )

        workout = generate_workout_gemini(
            user_data.username,
            user_data.age,
            user_data.weight,
            user_data.goal,
            user_data.intensity
        )

        nutrition_tip = (
            generate_nutrition_tip_with_flash(
                user_data.goal
            )
        )

        save_plan(
            user_data.user_id,
            workout,
            nutrition_tip
        )

        return templates.TemplateResponse(
            "result.html",
            {
                "request": request,
                "user": user_data,
                "workout": workout,
                "nutrition_tip": nutrition_tip,
                "updated": False
            }
        )

    except Exception as error:

        return templates.TemplateResponse(
            "index.html",
            {
                "request": request,
                "error": str(error)
            }
        )


@router.post(
    "/submit-feedback",
    response_class=HTMLResponse
)
def submit_feedback(
    request: Request,
    user_id: str = Form(...),
    feedback: str = Form(...)
):

    try:

        request_data = FeedbackRequest(
            user_id=user_id,
            feedback=feedback
        )

        user = get_user(request_data.user_id)
        plan = get_plan(request_data.user_id)

        if not user:
            raise ValueError(
                "User not found."
            )

        if not plan:
            raise ValueError(
                "No workout plan found."
            )

        updated = update_workout_plan(
            plan.original_plan,
            request_data.feedback
        )

        update_plan(
            request_data.user_id,
            updated,
            request_data.feedback
        )

        return templates.TemplateResponse(
            "result.html",
            {
                "request": request,
                "user": user,
                "workout": updated,
                "nutrition_tip": plan.nutrition_tip,
                "updated": True,
                "original_plan": plan.original_plan,
                "feedback": request_data.feedback
            }
        )

    except Exception as error:

        return templates.TemplateResponse(
            "feedback.html",
            {
                "request": request,
                "error": str(error)
            }
        )


@router.get(
    "/view-all-users",
    response_class=HTMLResponse
)
def view_all_users(request: Request):

    users = get_all_users()

    return templates.TemplateResponse(
        "all_users.html",
        {
            "request": request,
            "users": users
        }
    )


@router.post("/delete-user")
def remove_user(user_id: str = Form(...)):

    delete_user(user_id)

    return {
        "message": "User deleted successfully"
    }


@router.post("/api/generate-workout")
def api_generate_workout(data: UserInput):

    save_user(
        data.user_id,
        data.username,
        data.age,
        data.weight,
        data.goal,
        data.intensity
    )

    workout = generate_workout_gemini(
        data.username,
        data.age,
        data.weight,
        data.goal,
        data.intensity
    )

    tip = generate_nutrition_tip_with_flash(
        data.goal
    )

    save_plan(
        data.user_id,
        workout,
        tip
    )

    return {
        "user_id": data.user_id,
        "workout": workout,
        "nutrition_tip": tip
    }


@router.post("/api/submit-feedback")
def api_submit_feedback(data: FeedbackRequest):

    plan = get_plan(data.user_id)

    if not plan:
        return JSONResponse(
            status_code=404,
            content={
                "error": "Plan not found"
            }
        )

    updated = update_workout_plan(
        plan.original_plan,
        data.feedback
    )

    update_plan(
        data.user_id,
        updated,
        data.feedback
    )

    return {
        "user_id": data.user_id,
        "updated_plan": updated
    }


@router.get("/api/users")
def api_users():

    users = get_all_users()

    return [
        {
            "user_id": user.user_id,
            "username": user.username,
            "age": user.age,
            "weight": user.weight,
            "goal": user.goal,
            "intensity": user.intensity
        }
        for user in users
    ]


@router.get("/api/users/{user_id}")
def api_user(user_id: str):

    user = get_user(user_id)

    if not user:
        return JSONResponse(
            status_code=404,
            content={
                "error": "User not found"
            }
        )

    plan = get_plan(user_id)

    return {
        "user": {
            "user_id": user.user_id,
            "username": user.username,
            "age": user.age,
            "weight": user.weight,
            "goal": user.goal,
            "intensity": user.intensity
        },
        "plan": {
            "original_plan": plan.original_plan
            if plan else None,
            "updated_plan": plan.updated_plan
            if plan else None,
            "nutrition_tip": plan.nutrition_tip
            if plan else None,
            "feedback": plan.feedback
            if plan else None
        }
    }
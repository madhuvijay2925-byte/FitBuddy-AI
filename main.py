from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from .database import init_db
from .routes import router


app = FastAPI(
    title="FitBuddy – AI Fitness Plan Generator",
    description="AI-powered fitness planning application",
    version="1.0.0"
)


init_db()


app.mount(
    "/static",
    StaticFiles(directory="static"),
    name="static"
)


app.include_router(router)


@app.get("/health")
def health():

    return {
        "status": "ok",
        "service": "FitBuddy"
    }
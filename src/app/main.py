from fastapi import FastAPI
from app.core.settings import get_settings
from app.core.dependencies import get_db

settings = get_settings()

app = FastAPI(
    title=settings.API_NAME,
    version=settings.API_VERSION
)

@app.get("/")
async def read_root():
    return {"message": "Welcome to the Data Lineage Tracker API!"}


@app.get("/settings")
async def print_settings():
    return {
        "API Name": settings.API_NAME,
        "API Version": settings.API_VERSION,
        "Database URL": settings.DATABASE_URL
    }
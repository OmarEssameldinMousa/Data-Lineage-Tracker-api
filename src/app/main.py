from fastapi import FastAPI
from app.core.settings import get_settings
from app.core.dependencies import get_db
from app.api.routers.edges import router as edges_router
from app.api.routers.datasets import router as datasets_router
settings = get_settings()

app = FastAPI(
    title=settings.API_NAME,
    version=settings.API_VERSION
)
app.include_router(edges_router)

app.include_router(datasets_router)

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
from fastapi import APIRouter
from pydantic import BaseModel
from app.core.config import settings

router = APIRouter()


class HealthResponse(BaseModel):
    status: str
    app_name: str
    version: str
    environment: str


@router.get("/health", response_model=HealthResponse, summary="Get API Health Status")
async def get_health() -> HealthResponse:
    """
    Truthful system health check endpoint for Phase 0.1 foundation verification.
    Returns basic application status without fake metrics or mock data.
    """
    return HealthResponse(
        status="ok",
        app_name=settings.PROJECT_NAME,
        version=settings.VERSION,
        environment=settings.ENVIRONMENT,
    )

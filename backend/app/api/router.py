from fastapi import APIRouter
from app.api.endpoints import health, targets, workspaces

api_router = APIRouter()
api_router.include_router(health.router, tags=["Health"])
api_router.include_router(workspaces.router, prefix="/workspaces", tags=["Workspaces"])
api_router.include_router(targets.router, prefix="/targets", tags=["Targets"])

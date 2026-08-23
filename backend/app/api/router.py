from fastapi import APIRouter
from app.api.endpoints import authorization, health, scopes, security_operations, targets, workspaces

api_router = APIRouter()
api_router.include_router(health.router, tags=["Health"])
api_router.include_router(workspaces.router, prefix="/workspaces", tags=["Workspaces"])
api_router.include_router(targets.router, prefix="/targets", tags=["Targets"])
api_router.include_router(scopes.router, prefix="/scopes", tags=["Scopes"])
api_router.include_router(authorization.router, prefix="/authorization", tags=["Authorization Gateway"])
api_router.include_router(security_operations.router, prefix="/security-operations", tags=["Security Operations Framework"])

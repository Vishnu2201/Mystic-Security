from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field
from app.models.enums import ActivityType, AuthorizationLevel, SecurityOperationType


class AuthorizationCheckRequest(BaseModel):
    """Request schema for explicit security operation authorization check."""
    workspace_id: UUID = Field(..., description="UUID of the workspace context")
    target_id: UUID = Field(..., description="UUID of the target resource")
    operation_type: SecurityOperationType = Field(..., description="Type of security operation to authorize")


class AuthorizationCheckResponse(BaseModel):
    """Structured result returned by the central authorization gateway."""
    authorized: bool = Field(..., description="True if operation is authorized; False otherwise")
    workspace_id: UUID = Field(..., description="Workspace ID evaluated")
    target_id: Optional[UUID] = Field(None, description="Target ID evaluated")
    operation_type: SecurityOperationType = Field(..., description="Security operation evaluated")
    activity_type: Optional[ActivityType] = Field(None, description="Classified activity type (PASSIVE or ACTIVE)")
    authorization_level: Optional[AuthorizationLevel] = Field(None, description="Matched scope authorization level")
    reason: str = Field(..., description="Human-readable decision explanation")

from datetime import datetime
from typing import Any, Dict, Optional
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field
from app.models.enums import (
    ActivityType,
    AuthorizationLevel,
    SecurityOperationStatus,
    SecurityOperationType,
)


class SecurityOperationCreate(BaseModel):
    """Schema for requesting a new Security Operation execution."""
    workspace_id: UUID = Field(..., description="UUID of the parent workspace context")
    target_id: UUID = Field(..., description="UUID of the target resource")
    operation_type: SecurityOperationType = Field(..., description="Type of security operation to execute")
    parameters: Optional[Dict[str, Any]] = Field(None, description="Optional execution parameters")


class SecurityOperationResponse(BaseModel):
    """Schema for returning a Security Operation execution record."""
    id: UUID
    workspace_id: UUID
    target_id: UUID
    operation_type: SecurityOperationType
    activity_type: ActivityType
    status: SecurityOperationStatus
    authorization_level: Optional[AuthorizationLevel] = None
    authorization_reason: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = None
    requested_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    result: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

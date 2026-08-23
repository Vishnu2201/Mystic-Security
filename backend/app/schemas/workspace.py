from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field


class WorkspaceCreate(BaseModel):
    """Schema for creating a new Workspace."""
    name: str = Field(..., min_length=1, max_length=255, description="Unique workspace name")
    description: Optional[str] = Field(None, description="Optional workspace description")


class WorkspaceUpdate(BaseModel):
    """Schema for updating an existing Workspace."""
    name: Optional[str] = Field(None, min_length=1, max_length=255, description="Updated workspace name")
    description: Optional[str] = Field(None, description="Updated workspace description")


class WorkspaceResponse(BaseModel):
    """Schema for returning a Workspace resource."""
    id: UUID
    name: str
    description: Optional[str]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

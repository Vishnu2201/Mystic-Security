from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field, field_validator
from app.core.validators import (
    validate_workspace_name,
    validate_workspace_description,
)


class WorkspaceCreate(BaseModel):
    """Schema for creating a new Workspace."""
    name: str = Field(..., description="Unique workspace name")
    description: Optional[str] = Field(None, description="Optional workspace description")

    @field_validator("name")
    @classmethod
    def check_name(cls, v: str) -> str:
        return validate_workspace_name(v)

    @field_validator("description")
    @classmethod
    def check_description(cls, v: Optional[str]) -> Optional[str]:
        return validate_workspace_description(v)


class WorkspaceUpdate(BaseModel):
    """Schema for updating an existing Workspace."""
    name: Optional[str] = Field(None, description="Updated workspace name")
    description: Optional[str] = Field(None, description="Updated workspace description")

    @field_validator("name")
    @classmethod
    def check_name(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            raise ValueError("Workspace name cannot be null.")
        return validate_workspace_name(v)

    @field_validator("description")
    @classmethod
    def check_description(cls, v: Optional[str]) -> Optional[str]:
        return validate_workspace_description(v)


class WorkspaceResponse(BaseModel):
    """Schema for returning a Workspace resource."""
    id: UUID
    name: str
    description: Optional[str]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

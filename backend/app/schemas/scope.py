from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator
from app.models.enums import AuthorizationLevel, ScopeType
from app.core.validators import (
    validate_workspace_name,
    validate_workspace_description,
    validate_target_identifier,
)


class ScopeCreate(BaseModel):
    """Schema for creating a new Scope."""
    workspace_id: UUID = Field(..., description="UUID of the parent workspace")
    name: str = Field(..., description="Human-readable scope name")
    description: Optional[str] = Field(None, description="Optional scope description")
    scope_type: ScopeType = Field(..., description="Type of target pattern (DOMAIN, IP_ADDRESS, URL, NETWORK_RANGE, APPLICATION)")
    pattern: str = Field(..., description="Target pattern matching rule")
    authorization_level: AuthorizationLevel = Field(..., description="Authorization level (PASSIVE_ONLY, ACTIVE_ALLOWED, PROHIBITED)")
    is_active: bool = Field(True, description="Active status flag (defaults to true)")

    @field_validator("name")
    @classmethod
    def check_name(cls, v: str) -> str:
        return validate_workspace_name(v)

    @field_validator("description")
    @classmethod
    def check_description(cls, v: Optional[str]) -> Optional[str]:
        return validate_workspace_description(v)

    @model_validator(mode="after")
    def validate_pattern_against_type(self) -> "ScopeCreate":
        self.pattern = validate_target_identifier(self.scope_type, self.pattern)
        return self


class ScopeUpdate(BaseModel):
    """Schema for updating an existing Scope."""
    workspace_id: Optional[UUID] = Field(None, description="Updated parent workspace UUID")
    name: Optional[str] = Field(None, description="Updated scope name")
    description: Optional[str] = Field(None, description="Updated scope description")
    scope_type: Optional[ScopeType] = Field(None, description="Updated scope type")
    pattern: Optional[str] = Field(None, description="Updated scope pattern")
    authorization_level: Optional[AuthorizationLevel] = Field(None, description="Updated authorization level")
    is_active: Optional[bool] = Field(None, description="Updated active status flag")

    @field_validator("name")
    @classmethod
    def check_name(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            raise ValueError("Scope name cannot be null.")
        return validate_workspace_name(v)

    @field_validator("description")
    @classmethod
    def check_description(cls, v: Optional[str]) -> Optional[str]:
        return validate_workspace_description(v)

    @model_validator(mode="after")
    def validate_partial_fields(self) -> "ScopeUpdate":
        if "scope_type" in self.model_fields_set and self.scope_type is None:
            raise ValueError("Scope scope_type cannot be null.")
        if "pattern" in self.model_fields_set and self.pattern is None:
            raise ValueError("Scope pattern cannot be null.")
        if "authorization_level" in self.model_fields_set and self.authorization_level is None:
            raise ValueError("Scope authorization_level cannot be null.")
        if "is_active" in self.model_fields_set and self.is_active is None:
            raise ValueError("Scope is_active cannot be null.")

        if (
            "scope_type" in self.model_fields_set
            and "pattern" in self.model_fields_set
            and self.scope_type is not None
            and self.pattern is not None
        ):
            self.pattern = validate_target_identifier(self.scope_type, self.pattern)
        return self


class ScopeResponse(BaseModel):
    """Schema for returning a Scope resource."""
    id: UUID
    workspace_id: UUID
    name: str
    description: Optional[str]
    scope_type: ScopeType
    pattern: str
    authorization_level: AuthorizationLevel
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TargetAuthorizationResult(BaseModel):
    """Structured result returned by the target authorization check service."""
    authorized: bool
    authorization_level: Optional[AuthorizationLevel]
    matched_scope_id: Optional[UUID]
    reason: str

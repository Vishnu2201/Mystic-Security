from datetime import datetime
from typing import Any, Optional
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator
from app.models.enums import TargetCategory
from app.core.validators import (
    validate_target_identifier,
    validate_ip_address,
    validate_network_range,
)


class TargetCreate(BaseModel):
    """Schema for creating a new Target."""
    workspace_id: UUID = Field(..., description="UUID of the parent workspace")
    name: str = Field(..., min_length=1, max_length=255, description="Human-readable target name")
    target_category: TargetCategory = Field(..., description="Category classification (DOMAIN, IP_ADDRESS, URL, NETWORK_RANGE, APPLICATION)")
    identifier: str = Field(..., min_length=1, max_length=512, description="Normalized target identifier (e.g. domain, IP address, URL)")
    description: Optional[str] = Field(None, description="Optional target description")
    ip_address: Optional[str] = Field(None, description="Optional IPv4/IPv6 address")
    network_range: Optional[str] = Field(None, description="Optional CIDR block")

    @field_validator("ip_address")
    @classmethod
    def check_ip_address(cls, v: Optional[str]) -> Optional[str]:
        return validate_ip_address(v)

    @field_validator("network_range")
    @classmethod
    def check_network_range(cls, v: Optional[str]) -> Optional[str]:
        return validate_network_range(v)

    @model_validator(mode="after")
    def validate_identifier_against_category(self) -> "TargetCreate":
        self.identifier = validate_target_identifier(self.target_category, self.identifier)
        return self


class TargetUpdate(BaseModel):
    """Schema for updating an existing Target."""
    workspace_id: Optional[UUID] = Field(None, description="Updated parent workspace UUID")
    name: Optional[str] = Field(None, min_length=1, max_length=255, description="Updated target name")
    target_category: Optional[TargetCategory] = Field(None, description="Updated target category")
    identifier: Optional[str] = Field(None, min_length=1, max_length=512, description="Updated target identifier")
    description: Optional[str] = Field(None, description="Updated target description")
    ip_address: Optional[str] = Field(None, description="Updated IPv4/IPv6 address")
    network_range: Optional[str] = Field(None, description="Updated CIDR block")

    @field_validator("ip_address")
    @classmethod
    def check_ip_address(cls, v: Optional[str]) -> Optional[str]:
        return validate_ip_address(v)

    @field_validator("network_range")
    @classmethod
    def check_network_range(cls, v: Optional[str]) -> Optional[str]:
        return validate_network_range(v)

    @model_validator(mode="after")
    def validate_partial_fields(self) -> "TargetUpdate":
        if "target_category" in self.model_fields_set and self.target_category is None:
            raise ValueError("Target target_category cannot be null.")
        if "identifier" in self.model_fields_set and self.identifier is None:
            raise ValueError("Target identifier cannot be null.")

        # If both category and identifier are provided in PATCH payload, validate them together
        if (
            "target_category" in self.model_fields_set
            and "identifier" in self.model_fields_set
            and self.target_category is not None
            and self.identifier is not None
        ):
            self.identifier = validate_target_identifier(self.target_category, self.identifier)
        return self


class TargetResponse(BaseModel):
    """Schema for returning a Target resource."""
    id: UUID
    workspace_id: UUID
    name: str
    target_category: TargetCategory
    identifier: str
    description: Optional[str]
    ip_address: Optional[str]
    network_range: Optional[str]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

    @field_validator("ip_address", "network_range", mode="before")
    @classmethod
    def serialize_network_fields(cls, v: Any) -> Optional[str]:
        """Convert PostgreSQL INET/CIDR ORM objects (IPv4Address, IPv6Address, etc.) to string."""
        if v is None:
            return None
        return str(v)

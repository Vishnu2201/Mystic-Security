import datetime
import uuid
from typing import Any, Dict, Optional, TYPE_CHECKING
from sqlalchemy import Enum as SQLEnum, ForeignKey, Text, text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base_class import Base
from app.models.enums import (
    ActivityType,
    AuthorizationLevel,
    SecurityOperationStatus,
    SecurityOperationType,
)

if TYPE_CHECKING:
    from app.models.workspace import Workspace
    from app.models.target import Target


class SecurityOperation(Base):
    """
    SecurityOperation persistent entity (Phase 0.9).
    Tracks requested, authorized, running, completed, failed, or denied security execution jobs.
    """
    __tablename__ = "security_operations"

    workspace_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("workspaces.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    target_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("targets.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    operation_type: Mapped[SecurityOperationType] = mapped_column(
        SQLEnum(SecurityOperationType, name="security_operation_type_enum"),
        nullable=False,
    )
    activity_type: Mapped[ActivityType] = mapped_column(
        SQLEnum(ActivityType, name="activity_type_enum"),
        nullable=False,
    )
    status: Mapped[SecurityOperationStatus] = mapped_column(
        SQLEnum(SecurityOperationStatus, name="security_operation_status_enum"),
        nullable=False,
        index=True,
    )

    authorization_level: Mapped[Optional[AuthorizationLevel]] = mapped_column(
        SQLEnum(AuthorizationLevel, name="authorization_level_enum"),
        nullable=True,
    )
    authorization_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    parameters: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB, nullable=True)

    requested_at: Mapped[datetime.datetime] = mapped_column(
        server_default=text("now()"),
        nullable=False,
    )
    started_at: Mapped[Optional[datetime.datetime]] = mapped_column(nullable=True)
    completed_at: Mapped[Optional[datetime.datetime]] = mapped_column(nullable=True)

    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    result: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB, nullable=True)

    # Relationships
    workspace: Mapped["Workspace"] = relationship("Workspace", back_populates="security_operations")
    target: Mapped["Target"] = relationship("Target", back_populates="security_operations")

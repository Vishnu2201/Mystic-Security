import uuid
from datetime import datetime, timezone
from typing import List, TYPE_CHECKING
from sqlalchemy import CheckConstraint, DateTime, Enum as SQLEnum, ForeignKey, Index, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base_class import Base
from app.models.enums import AuthorizationStatus
from app.models.associations import authorization_targets, authorization_scopes

if TYPE_CHECKING:
    from app.models.workspace import Workspace
    from app.models.target import Target
    from app.models.scope import Scope
    from app.models.assessment import Assessment


class Authorization(Base):
    """
    Authorization persistent entity.
    Independent Workspace-level consent record granting permission to perform security testing.
    Can govern multiple Targets and Scopes.
    """
    __tablename__ = "authorizations"
    __table_args__ = (
        CheckConstraint("valid_from <= valid_until", name="check_valid_authorization_dates"),
        UniqueConstraint("workspace_id", "reference_code", name="uq_authorizations_workspace_refcode"),
        Index("ix_authorizations_validity", "workspace_id", "persisted_status", "valid_from", "valid_until"),
    )

    workspace_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("workspaces.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    reference_code: Mapped[str] = mapped_column(String(255), nullable=False)
    persisted_status: Mapped[AuthorizationStatus] = mapped_column(
        SQLEnum(AuthorizationStatus, name="authorization_status_enum"),
        default=AuthorizationStatus.DRAFT,
        nullable=False,
    )
    valid_from: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    valid_until: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relationships
    workspace: Mapped["Workspace"] = relationship("Workspace", back_populates="authorizations")
    targets: Mapped[List["Target"]] = relationship(
        "Target",
        secondary=authorization_targets,
        back_populates="authorizations",
    )
    scopes: Mapped[List["Scope"]] = relationship(
        "Scope",
        secondary=authorization_scopes,
        back_populates="authorizations",
    )
    assessments: Mapped[List["Assessment"]] = relationship("Assessment", back_populates="authorization")

    @property
    def is_currently_valid(self) -> bool:
        """
        Calculates effective validity dynamically at runtime.
        True ONLY if persisted_status == ACTIVE and valid_from <= now <= valid_until.
        """
        now = datetime.now(timezone.utc)
        return (
            self.persisted_status == AuthorizationStatus.ACTIVE
            and self.valid_from <= now <= self.valid_until
        )

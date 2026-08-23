import uuid
from typing import Any, Dict, List, TYPE_CHECKING
from sqlalchemy import Enum as SQLEnum, ForeignKey, Index, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base_class import Base
from app.models.enums import AssessmentMode, AssessmentStatus

if TYPE_CHECKING:
    from app.models.workspace import Workspace
    from app.models.target import Target
    from app.models.authorization import Authorization
    from app.models.scope import Scope
    from app.models.asset import Asset
    from app.models.observation import Observation
    from app.models.finding import Finding
    from app.models.evidence import Evidence
    from app.models.report import Report


class Assessment(Base):
    """
    Assessment persistent entity.
    Central historical execution entity binding Target, Authorization, Scope, and Execution Snapshot context.
    """
    __tablename__ = "assessments"
    __table_args__ = (
        Index("ix_assessments_workspace_status", "workspace_id", "status"),
    )

    workspace_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("workspaces.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    target_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("targets.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    authorization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("authorizations.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    scope_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("scopes.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    assessment_mode: Mapped[AssessmentMode] = mapped_column(
        SQLEnum(AssessmentMode, name="assessment_mode_enum"),
        default=AssessmentMode.FAST,
        nullable=False,
    )
    status: Mapped[AssessmentStatus] = mapped_column(
        SQLEnum(AssessmentStatus, name="assessment_status_enum"),
        default=AssessmentStatus.DRAFT,
        nullable=False,
    )

    # Immutable Execution Context Snapshot (JSONB payload populated upon queueing)
    execution_snapshot: Mapped[Dict[str, Any] | None] = mapped_column(
        JSONB,
        nullable=True,
        comment="Immutable frozen execution context containing Target, Authorization, Scope, Mode, Policy, and Plan DAG snapshots.",
    )

    # Relationships
    workspace: Mapped["Workspace"] = relationship("Workspace", back_populates="assessments")
    target: Mapped["Target"] = relationship("Target", back_populates="assessments")
    authorization: Mapped["Authorization"] = relationship("Authorization", back_populates="assessments")
    scope: Mapped["Scope"] = relationship("Scope", back_populates="assessments")

    assets: Mapped[List["Asset"]] = relationship("Asset", back_populates="assessment", cascade="all, delete-orphan")
    observations: Mapped[List["Observation"]] = relationship("Observation", back_populates="assessment", cascade="all, delete-orphan")
    findings: Mapped[List["Finding"]] = relationship("Finding", back_populates="assessment", cascade="all, delete-orphan")
    evidence_records: Mapped[List["Evidence"]] = relationship("Evidence", back_populates="assessment", cascade="all, delete-orphan")
    reports: Mapped[List["Report"]] = relationship("Report", back_populates="assessment", cascade="all, delete-orphan")

import uuid
from typing import List, TYPE_CHECKING
from sqlalchemy import Enum as SQLEnum, ForeignKey, Index, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base_class import Base
from app.models.enums import FindingSeverity, FindingStatus
from app.models.associations import finding_observations, finding_evidence

if TYPE_CHECKING:
    from app.models.workspace import Workspace
    from app.models.assessment import Assessment
    from app.models.observation import Observation
    from app.models.evidence import Evidence


class Finding(Base):
    """
    Finding persistent entity.
    Represents a verified security-relevant conclusion (vulnerability, misconfiguration, weakness).
    Traceable to supporting Observations and/or Evidence records.
    """
    __tablename__ = "findings"
    __table_args__ = (
        Index("ix_findings_workspace_severity", "workspace_id", "severity"),
        Index("ix_findings_workspace_status", "workspace_id", "status"),
    )

    workspace_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("workspaces.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    assessment_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("assessments.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    severity: Mapped[FindingSeverity] = mapped_column(
        SQLEnum(FindingSeverity, name="finding_severity_enum"),
        default=FindingSeverity.INFO,
        nullable=False,
    )
    status: Mapped[FindingStatus] = mapped_column(
        SQLEnum(FindingStatus, name="finding_status_enum"),
        default=FindingStatus.UNVERIFIED,
        nullable=False,
    )

    # Relationships
    workspace: Mapped["Workspace"] = relationship("Workspace", back_populates="findings")
    assessment: Mapped["Assessment"] = relationship("Assessment", back_populates="findings")
    observations: Mapped[List["Observation"]] = relationship(
        "Observation",
        secondary=finding_observations,
        back_populates="findings",
    )
    evidence_records: Mapped[List["Evidence"]] = relationship(
        "Evidence",
        secondary=finding_evidence,
        back_populates="findings",
    )

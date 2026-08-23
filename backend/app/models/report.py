import uuid
from typing import TYPE_CHECKING
from sqlalchemy import Enum as SQLEnum, ForeignKey, Index, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base_class import Base
from app.models.enums import ReportStatus

if TYPE_CHECKING:
    from app.models.workspace import Workspace
    from app.models.assessment import Assessment


class Report(Base):
    """
    Report persistent entity.
    Metadata model representing an exported, point-in-time assessment report document.
    """
    __tablename__ = "reports"
    __table_args__ = (
        Index("ix_reports_workspace_status", "workspace_id", "report_status"),
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
    report_status: Mapped[ReportStatus] = mapped_column(
        SQLEnum(ReportStatus, name="report_status_enum"),
        default=ReportStatus.GENERATING,
        nullable=False,
    )

    # Relationships
    workspace: Mapped["Workspace"] = relationship("Workspace", back_populates="reports")
    assessment: Mapped["Assessment"] = relationship("Assessment", back_populates="reports")

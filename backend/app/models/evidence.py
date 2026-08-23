import uuid
from typing import List, TYPE_CHECKING
from sqlalchemy import ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base_class import Base
from app.models.associations import finding_evidence

if TYPE_CHECKING:
    from app.models.workspace import Workspace
    from app.models.assessment import Assessment
    from app.models.finding import Finding


class Evidence(Base):
    """
    Evidence persistent entity.
    Represents metadata and storage references for immutable evidence payloads (e.g. MinIO/S3 objects).
    """
    __tablename__ = "evidence"

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
    storage_location: Mapped[str] = mapped_column(String(512), nullable=False, index=True)
    content_checksum: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True, comment="Cryptographic SHA256 checksum for integrity verification.")
    content_type: Mapped[str | None] = mapped_column(String(128), nullable=True)

    # Relationships
    workspace: Mapped["Workspace"] = relationship("Workspace", back_populates="evidence_records")
    assessment: Mapped["Assessment"] = relationship("Assessment", back_populates="evidence_records")
    findings: Mapped[List["Finding"]] = relationship(
        "Finding",
        secondary=finding_evidence,
        back_populates="evidence_records",
    )

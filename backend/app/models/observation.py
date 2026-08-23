import uuid
from typing import Any, Dict, List, TYPE_CHECKING
from sqlalchemy import Enum as SQLEnum, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import INET, JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base_class import Base
from app.models.associations import finding_observations

if TYPE_CHECKING:
    from app.models.workspace import Workspace
    from app.models.assessment import Assessment
    from app.models.asset import Asset
    from app.models.finding import Finding


class Observation(Base):
    """
    Observation persistent entity.
    Represents an atomic empirical fact extracted from execution output.
    Uses a hybrid model (relational indexed fields + provider_payload JSONB).
    """
    __tablename__ = "observations"

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
    asset_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("assets.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    observation_type: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    subject_identifier: Mapped[str] = mapped_column(String(512), nullable=False, index=True)

    # Relational queryable fields
    domain_name: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    ip_address: Mapped[str | None] = mapped_column(INET, nullable=True, index=True)
    service_port: Mapped[int | None] = mapped_column(Integer, nullable=True, index=True)

    # Tool/provider-specific JSON payload
    provider_payload: Mapped[Dict[str, Any] | None] = mapped_column(JSONB, nullable=True)

    # Relationships
    workspace: Mapped["Workspace"] = relationship("Workspace", back_populates="observations")
    assessment: Mapped["Assessment"] = relationship("Assessment", back_populates="observations")
    asset: Mapped["Asset | None"] = relationship("Asset", back_populates="observations")
    findings: Mapped[List["Finding"]] = relationship(
        "Finding",
        secondary=finding_observations,
        back_populates="observations",
    )

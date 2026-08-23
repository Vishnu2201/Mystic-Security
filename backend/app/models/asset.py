import uuid
from typing import List, TYPE_CHECKING
from sqlalchemy import Enum as SQLEnum, ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import INET, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base_class import Base
from app.models.enums import AssetType

if TYPE_CHECKING:
    from app.models.workspace import Workspace
    from app.models.assessment import Assessment
    from app.models.target import Target
    from app.models.observation import Observation


class Asset(Base):
    """
    Asset persistent entity.
    Represents a verified empirical host, domain, IP address, service, or application identified during authorized testing.
    """
    __tablename__ = "assets"
    __table_args__ = (
        UniqueConstraint("assessment_id", "identifier", name="uq_assets_assessment_identifier"),
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
    target_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("targets.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    asset_type: Mapped[AssetType] = mapped_column(
        SQLEnum(AssetType, name="asset_type_enum"),
        nullable=False,
    )
    identifier: Mapped[str] = mapped_column(String(512), nullable=False)
    ip_address: Mapped[str | None] = mapped_column(INET, nullable=True)

    # Relationships
    workspace: Mapped["Workspace"] = relationship("Workspace", back_populates="assets")
    assessment: Mapped["Assessment"] = relationship("Assessment", back_populates="assets")
    target: Mapped["Target | None"] = relationship("Target", back_populates="assets")
    observations: Mapped[List["Observation"]] = relationship("Observation", back_populates="asset")

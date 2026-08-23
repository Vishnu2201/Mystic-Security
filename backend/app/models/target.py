import uuid
from typing import List, TYPE_CHECKING
from sqlalchemy import Enum as SQLEnum, ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import CIDR, INET, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base_class import Base
from app.models.enums import TargetCategory
from app.models.associations import authorization_targets

if TYPE_CHECKING:
    from app.models.workspace import Workspace
    from app.models.authorization import Authorization
    from app.models.assessment import Assessment
    from app.models.asset import Asset


class Target(Base):
    """
    Target persistent entity.
    Represents an empirical physical or logical subject intended for security evaluation.
    Independent Workspace-level entity; presence of Target does NOT grant authorization.
    """
    __tablename__ = "targets"
    __table_args__ = (
        UniqueConstraint("workspace_id", "identifier", name="uq_targets_workspace_identifier"),
    )

    workspace_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("workspaces.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    target_category: Mapped[TargetCategory] = mapped_column(
        SQLEnum(TargetCategory, name="target_category_enum"),
        nullable=False,
    )
    identifier: Mapped[str] = mapped_column(String(512), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    # PostgreSQL native network types
    ip_address: Mapped[str | None] = mapped_column(INET, nullable=True)
    network_range: Mapped[str | None] = mapped_column(CIDR, nullable=True)

    # Relationships
    workspace: Mapped["Workspace"] = relationship("Workspace", back_populates="targets")
    authorizations: Mapped[List["Authorization"]] = relationship(
        "Authorization",
        secondary=authorization_targets,
        back_populates="targets",
    )
    assessments: Mapped[List["Assessment"]] = relationship("Assessment", back_populates="target")
    assets: Mapped[List["Asset"]] = relationship("Asset", back_populates="target")

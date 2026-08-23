from typing import List, TYPE_CHECKING
from sqlalchemy import String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base_class import Base

if TYPE_CHECKING:
    from app.models.target import Target
    from app.models.authorization import Authorization
    from app.models.scope import Scope
    from app.models.assessment import Assessment
    from app.models.asset import Asset
    from app.models.observation import Observation
    from app.models.finding import Finding
    from app.models.evidence import Evidence
    from app.models.report import Report


class Workspace(Base):
    """
    Workspace persistent entity.
    Top-level organizational data isolation boundary.
    """
    __tablename__ = "workspaces"
    __table_args__ = (
        UniqueConstraint("name", name="uq_workspaces_name"),
    )

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relationships to child domain entities
    targets: Mapped[List["Target"]] = relationship("Target", back_populates="workspace", cascade="all, delete-orphan")
    authorizations: Mapped[List["Authorization"]] = relationship("Authorization", back_populates="workspace", cascade="all, delete-orphan")
    scopes: Mapped[List["Scope"]] = relationship("Scope", back_populates="workspace", cascade="all, delete-orphan")
    assessments: Mapped[List["Assessment"]] = relationship("Assessment", back_populates="workspace", cascade="all, delete-orphan")
    assets: Mapped[List["Asset"]] = relationship("Asset", back_populates="workspace", cascade="all, delete-orphan")
    observations: Mapped[List["Observation"]] = relationship("Observation", back_populates="workspace", cascade="all, delete-orphan")
    findings: Mapped[List["Finding"]] = relationship("Finding", back_populates="workspace", cascade="all, delete-orphan")
    evidence_records: Mapped[List["Evidence"]] = relationship("Evidence", back_populates="workspace", cascade="all, delete-orphan")
    reports: Mapped[List["Report"]] = relationship("Report", back_populates="workspace", cascade="all, delete-orphan")

import uuid
from typing import List, TYPE_CHECKING
from sqlalchemy import Boolean, Enum as SQLEnum, ForeignKey, String, Text, UniqueConstraint, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base_class import Base
from app.models.enums import AuthorizationLevel, ScopeRuleAction, ScopeRuleCategory, ScopeType
from app.models.associations import authorization_scopes

if TYPE_CHECKING:
    from app.models.workspace import Workspace
    from app.models.authorization import Authorization
    from app.models.assessment import Assessment


class Scope(Base):
    """
    Scope persistent entity for Phase 0.7.
    Defines explicit workspace-level target inclusion, exclusion, and authorization rules.
    """
    __tablename__ = "scopes"
    __table_args__ = (
        UniqueConstraint("workspace_id", "scope_type", "pattern", name="uq_scopes_workspace_type_pattern"),
    )

    workspace_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("workspaces.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    scope_type: Mapped[ScopeType] = mapped_column(
        SQLEnum(ScopeType, name="scope_type_enum"),
        nullable=False,
    )
    pattern: Mapped[str] = mapped_column(String(512), nullable=False)

    authorization_level: Mapped[AuthorizationLevel] = mapped_column(
        SQLEnum(AuthorizationLevel, name="authorization_level_enum"),
        nullable=False,
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        server_default=text("true"),
        nullable=False,
    )

    # Relationships
    workspace: Mapped["Workspace"] = relationship("Workspace", back_populates="scopes")
    rules: Mapped[List["ScopeRule"]] = relationship(
        "ScopeRule",
        back_populates="scope",
        cascade="all, delete-orphan",
    )
    authorizations: Mapped[List["Authorization"]] = relationship(
        "Authorization",
        secondary=authorization_scopes,
        back_populates="scopes",
    )
    assessments: Mapped[List["Assessment"]] = relationship("Assessment", back_populates="scope")


class ScopeRule(Base):
    """
    ScopeRule child entity.
    Relational inclusion or exclusion rule governing target execution boundaries.
    """
    __tablename__ = "scope_rules"

    scope_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("scopes.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    rule_action: Mapped[ScopeRuleAction] = mapped_column(
        SQLEnum(ScopeRuleAction, name="scope_rule_action_enum"),
        nullable=False,
    )
    rule_category: Mapped[ScopeRuleCategory] = mapped_column(
        SQLEnum(ScopeRuleCategory, name="scope_rule_category_enum"),
        nullable=False,
    )
    pattern: Mapped[str] = mapped_column(String(512), nullable=False)

    # Relationships
    scope: Mapped["Scope"] = relationship("Scope", back_populates="rules")

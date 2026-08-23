import uuid
from datetime import datetime
from sqlalchemy import Column, DateTime, ForeignKey, Table, func
from sqlalchemy.dialects.postgresql import UUID
from app.db.base_class import Base

# Association Table: Authorization <-> Target (Multi-target authorization coverage)
authorization_targets = Table(
    "authorization_targets",
    Base.metadata,
    Column("authorization_id", UUID(as_uuid=True), ForeignKey("authorizations.id", ondelete="CASCADE"), primary_key=True),
    Column("target_id", UUID(as_uuid=True), ForeignKey("targets.id", ondelete="CASCADE"), primary_key=True),
    Column("created_at", DateTime(timezone=True), server_default=func.now(), nullable=False),
)

# Association Table: Authorization <-> Scope (Multi-scope authorization coverage)
authorization_scopes = Table(
    "authorization_scopes",
    Base.metadata,
    Column("authorization_id", UUID(as_uuid=True), ForeignKey("authorizations.id", ondelete="CASCADE"), primary_key=True),
    Column("scope_id", UUID(as_uuid=True), ForeignKey("scopes.id", ondelete="CASCADE"), primary_key=True),
    Column("created_at", DateTime(timezone=True), server_default=func.now(), nullable=False),
)

# Association Table: Finding <-> Observation (Flexible finding traceability)
finding_observations = Table(
    "finding_observations",
    Base.metadata,
    Column("finding_id", UUID(as_uuid=True), ForeignKey("findings.id", ondelete="CASCADE"), primary_key=True),
    Column("observation_id", UUID(as_uuid=True), ForeignKey("observations.id", ondelete="CASCADE"), primary_key=True),
    Column("created_at", DateTime(timezone=True), server_default=func.now(), nullable=False),
)

# Association Table: Finding <-> Evidence (Flexible finding evidence traceability)
finding_evidence = Table(
    "finding_evidence",
    Base.metadata,
    Column("finding_id", UUID(as_uuid=True), ForeignKey("findings.id", ondelete="CASCADE"), primary_key=True),
    Column("evidence_id", UUID(as_uuid=True), ForeignKey("evidence.id", ondelete="CASCADE"), primary_key=True),
    Column("created_at", DateTime(timezone=True), server_default=func.now(), nullable=False),
)

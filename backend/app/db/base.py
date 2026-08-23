"""
Imports all SQLAlchemy models so that Base.metadata contains all model definitions.
Used by Alembic in env.py to generate migrations automatically.
"""

from app.db.base_class import Base  # noqa
from app.models import (  # noqa
    Workspace,
    Target,
    Authorization,
    Scope,
    ScopeRule,
    Assessment,
    Asset,
    Observation,
    Finding,
    Evidence,
    Report,
    authorization_targets,
    authorization_scopes,
    finding_observations,
    finding_evidence,
)

"""Add Phase 0.7 Scope Model and Authorization Fields

Revision ID: 002_add_phase_0_7_scope_model
Revises: 001_initial_domain_schema
Create Date: 2026-08-23 17:45:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '002_add_phase_0_7_scope_model'
down_revision: Union[str, None] = '001_initial_domain_schema'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# Single module-level PostgreSQL Enum definitions (create_type=False prevents automatic duplicate creation)
scope_type_enum = postgresql.ENUM(
    'DOMAIN',
    'IP_ADDRESS',
    'URL',
    'NETWORK_RANGE',
    'APPLICATION',
    name='scope_type_enum',
    create_type=False,
)

authorization_level_enum = postgresql.ENUM(
    'PASSIVE_ONLY',
    'ACTIVE_ALLOWED',
    'PROHIBITED',
    name='authorization_level_enum',
    create_type=False,
)


def upgrade() -> None:
    # Drop existing initial scopes table if present to apply Phase 0.7 schema clean rebuild
    op.execute('DROP TABLE IF EXISTS scopes CASCADE;')

    # Create Enums explicitly once
    scope_type_enum.create(op.get_bind(), checkfirst=True)
    authorization_level_enum.create(op.get_bind(), checkfirst=True)

    # Create Scopes table
    op.create_table(
        'scopes',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('workspace_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('workspaces.id', ondelete='CASCADE'), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('scope_type', scope_type_enum, nullable=False),
        sa.Column('pattern', sa.String(length=512), nullable=False),
        sa.Column('authorization_level', authorization_level_enum, nullable=False),
        sa.Column('is_active', sa.Boolean(), server_default=sa.text('true'), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.UniqueConstraint('workspace_id', 'scope_type', 'pattern', name='uq_scopes_workspace_type_pattern'),
    )
    op.create_index(op.f('ix_scopes_workspace_id'), 'scopes', ['workspace_id'], unique=False)
    op.create_index('ix_scopes_workspace_type_pattern', 'scopes', ['workspace_id', 'scope_type', 'pattern'], unique=False)
    op.create_index('ix_scopes_authorization', 'scopes', ['workspace_id', 'is_active', 'authorization_level'], unique=False)


def downgrade() -> None:
    op.drop_table('scopes')
    authorization_level_enum.drop(op.get_bind(), checkfirst=True)
    scope_type_enum.drop(op.get_bind(), checkfirst=True)

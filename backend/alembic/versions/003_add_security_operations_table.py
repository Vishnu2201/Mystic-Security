"""Add Security Operations Table

Revision ID: 003_security_operations
Revises: 002_add_phase_0_7_scope_model
Create Date: 2026-08-23 17:55:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '003_security_operations'
down_revision: Union[str, None] = '002_add_phase_0_7_scope_model'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# Single module-level PostgreSQL Enum definitions
security_operation_type_enum = postgresql.ENUM(
    'PASSIVE_RECON',
    'ACTIVE_RECON',
    'PORT_SCAN',
    'VULNERABILITY_SCAN',
    'WEB_SCAN',
    'CUSTOM',
    name='security_operation_type_enum',
    create_type=False,
)

activity_type_enum = postgresql.ENUM(
    'PASSIVE',
    'ACTIVE',
    name='activity_type_enum',
    create_type=False,
)

authorization_level_enum = postgresql.ENUM(
    'PASSIVE_ONLY',
    'ACTIVE_ALLOWED',
    'PROHIBITED',
    name='authorization_level_enum',
    create_type=False,
)

security_operation_status_enum = postgresql.ENUM(
    'PENDING',
    'AUTHORIZED',
    'RUNNING',
    'COMPLETED',
    'FAILED',
    'DENIED',
    name='security_operation_status_enum',
    create_type=False,
)


def upgrade() -> None:
    # Explicitly create all required enums if checkfirst=True
    security_operation_type_enum.create(op.get_bind(), checkfirst=True)
    activity_type_enum.create(op.get_bind(), checkfirst=True)
    authorization_level_enum.create(op.get_bind(), checkfirst=True)
    security_operation_status_enum.create(op.get_bind(), checkfirst=True)

    # Create security_operations table
    op.create_table(
        'security_operations',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('workspace_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('workspaces.id', ondelete='CASCADE'), nullable=False),
        sa.Column('target_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('targets.id', ondelete='CASCADE'), nullable=False),
        sa.Column('operation_type', security_operation_type_enum, nullable=False),
        sa.Column('activity_type', activity_type_enum, nullable=False),
        sa.Column('status', security_operation_status_enum, nullable=False),
        sa.Column('authorization_level', authorization_level_enum, nullable=True),
        sa.Column('authorization_reason', sa.Text(), nullable=True),
        sa.Column('parameters', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('requested_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('result', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    )
    op.create_index(op.f('ix_security_operations_workspace_id'), 'security_operations', ['workspace_id'], unique=False)
    op.create_index(op.f('ix_security_operations_target_id'), 'security_operations', ['target_id'], unique=False)
    op.create_index(op.f('ix_security_operations_status'), 'security_operations', ['status'], unique=False)


def downgrade() -> None:
    op.drop_table('security_operations')
    security_operation_status_enum.drop(op.get_bind(), checkfirst=True)

"""Initial Domain Schema for Phase 0.3

Revision ID: 001_initial_domain_schema
Revises: 
Create Date: 2026-08-23 16:30:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '001_initial_domain_schema'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# Single module-level PostgreSQL Enum definitions (create_type=False prevents automatic duplicate creation during table DDL)
target_category_enum = postgresql.ENUM(
    'DOMAIN',
    'IP_ADDRESS',
    'URL',
    'NETWORK_RANGE',
    'APPLICATION',
    name='target_category_enum',
    create_type=False,
)

authorization_status_enum = postgresql.ENUM(
    'DRAFT',
    'PENDING',
    'ACTIVE',
    'REVOKED',
    name='authorization_status_enum',
    create_type=False,
)

scope_rule_action_enum = postgresql.ENUM(
    'INCLUDE',
    'EXCLUDE',
    name='scope_rule_action_enum',
    create_type=False,
)

scope_rule_category_enum = postgresql.ENUM(
    'DOMAIN',
    'SUBDOMAIN_PATTERN',
    'URL',
    'IP_ADDRESS',
    'CIDR_RANGE',
    'APPLICATION',
    name='scope_rule_category_enum',
    create_type=False,
)

assessment_mode_enum = postgresql.ENUM(
    'FAST',
    'BALANCED',
    'THOROUGH',
    'CUSTOM',
    name='assessment_mode_enum',
    create_type=False,
)

assessment_status_enum = postgresql.ENUM(
    'DRAFT',
    'READY',
    'QUEUED',
    'RUNNING',
    'CANCELLED',
    'COMPLETED',
    'FAILED',
    name='assessment_status_enum',
    create_type=False,
)

asset_type_enum = postgresql.ENUM(
    'DOMAIN',
    'HOST',
    'IP_ADDRESS',
    'SERVICE',
    'APPLICATION',
    name='asset_type_enum',
    create_type=False,
)

finding_severity_enum = postgresql.ENUM(
    'CRITICAL',
    'HIGH',
    'MEDIUM',
    'LOW',
    'INFO',
    name='finding_severity_enum',
    create_type=False,
)

finding_status_enum = postgresql.ENUM(
    'UNVERIFIED',
    'CONFIRMED',
    'FALSE_POSITIVE',
    'REMEDIATED',
    'ACCEPTED_RISK',
    name='finding_status_enum',
    create_type=False,
)

report_status_enum = postgresql.ENUM(
    'GENERATING',
    'PUBLISHED',
    'ARCHIVED',
    name='report_status_enum',
    create_type=False,
)


def upgrade() -> None:
    # 1. Explicit single creation path for each PostgreSQL enum type
    target_category_enum.create(op.get_bind(), checkfirst=True)
    authorization_status_enum.create(op.get_bind(), checkfirst=True)
    scope_rule_action_enum.create(op.get_bind(), checkfirst=True)
    scope_rule_category_enum.create(op.get_bind(), checkfirst=True)
    assessment_mode_enum.create(op.get_bind(), checkfirst=True)
    assessment_status_enum.create(op.get_bind(), checkfirst=True)
    asset_type_enum.create(op.get_bind(), checkfirst=True)
    finding_severity_enum.create(op.get_bind(), checkfirst=True)
    finding_status_enum.create(op.get_bind(), checkfirst=True)
    report_status_enum.create(op.get_bind(), checkfirst=True)

    # 2. Create Tables referencing module-level enum objects directly
    # Workspaces
    op.create_table(
        'workspaces',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.UniqueConstraint('name', name='uq_workspaces_name'),
    )

    # Targets
    op.create_table(
        'targets',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('workspace_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('workspaces.id', ondelete='CASCADE'), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('target_category', target_category_enum, nullable=False),
        sa.Column('identifier', sa.String(length=512), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('ip_address', postgresql.INET(), nullable=True),
        sa.Column('network_range', postgresql.CIDR(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.UniqueConstraint('workspace_id', 'identifier', name='uq_targets_workspace_identifier'),
    )
    op.create_index(op.f('ix_targets_workspace_id'), 'targets', ['workspace_id'], unique=False)

    # Authorizations
    op.create_table(
        'authorizations',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('workspace_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('workspaces.id', ondelete='CASCADE'), nullable=False),
        sa.Column('reference_code', sa.String(length=255), nullable=False),
        sa.Column('persisted_status', authorization_status_enum, nullable=False),
        sa.Column('valid_from', sa.DateTime(timezone=True), nullable=False),
        sa.Column('valid_until', sa.DateTime(timezone=True), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.CheckConstraint('valid_from <= valid_until', name='check_valid_authorization_dates'),
        sa.UniqueConstraint('workspace_id', 'reference_code', name='uq_authorizations_workspace_refcode'),
    )
    op.create_index(op.f('ix_authorizations_workspace_id'), 'authorizations', ['workspace_id'], unique=False)
    op.create_index('ix_authorizations_validity', 'authorizations', ['workspace_id', 'persisted_status', 'valid_from', 'valid_until'], unique=False)

    # Scopes
    op.create_table(
        'scopes',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('workspace_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('workspaces.id', ondelete='CASCADE'), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.UniqueConstraint('workspace_id', 'name', name='uq_scopes_workspace_name'),
    )
    op.create_index(op.f('ix_scopes_workspace_id'), 'scopes', ['workspace_id'], unique=False)

    # Scope Rules
    op.create_table(
        'scope_rules',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('scope_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('scopes.id', ondelete='CASCADE'), nullable=False),
        sa.Column('rule_action', scope_rule_action_enum, nullable=False),
        sa.Column('rule_category', scope_rule_category_enum, nullable=False),
        sa.Column('pattern', sa.String(length=512), nullable=False),
        sa.Column('ip_address', postgresql.INET(), nullable=True),
        sa.Column('cidr_range', postgresql.CIDR(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    )
    op.create_index(op.f('ix_scope_rules_scope_id'), 'scope_rules', ['scope_id'], unique=False)

    # Assessments
    op.create_table(
        'assessments',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('workspace_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('workspaces.id', ondelete='CASCADE'), nullable=False),
        sa.Column('target_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('targets.id', ondelete='RESTRICT'), nullable=False),
        sa.Column('authorization_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('authorizations.id', ondelete='RESTRICT'), nullable=False),
        sa.Column('scope_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('scopes.id', ondelete='RESTRICT'), nullable=False),
        sa.Column('assessment_mode', assessment_mode_enum, nullable=False),
        sa.Column('status', assessment_status_enum, nullable=False),
        sa.Column('execution_snapshot', postgresql.JSONB(astext_type=sa.Text()), nullable=True, comment='Immutable frozen execution context containing Target, Authorization, Scope, Mode, Policy, and Plan DAG snapshots.'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    )
    op.create_index(op.f('ix_assessments_workspace_id'), 'assessments', ['workspace_id'], unique=False)
    op.create_index(op.f('ix_assessments_target_id'), 'assessments', ['target_id'], unique=False)
    op.create_index(op.f('ix_assessments_authorization_id'), 'assessments', ['authorization_id'], unique=False)
    op.create_index(op.f('ix_assessments_scope_id'), 'assessments', ['scope_id'], unique=False)
    op.create_index('ix_assessments_workspace_status', 'assessments', ['workspace_id', 'status'], unique=False)

    # Assets
    op.create_table(
        'assets',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('workspace_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('workspaces.id', ondelete='CASCADE'), nullable=False),
        sa.Column('assessment_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('assessments.id', ondelete='CASCADE'), nullable=False),
        sa.Column('target_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('targets.id', ondelete='SET NULL'), nullable=True),
        sa.Column('asset_type', asset_type_enum, nullable=False),
        sa.Column('identifier', sa.String(length=512), nullable=False),
        sa.Column('ip_address', postgresql.INET(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.UniqueConstraint('assessment_id', 'identifier', name='uq_assets_assessment_identifier'),
    )
    op.create_index(op.f('ix_assets_workspace_id'), 'assets', ['workspace_id'], unique=False)
    op.create_index(op.f('ix_assets_assessment_id'), 'assets', ['assessment_id'], unique=False)
    op.create_index(op.f('ix_assets_target_id'), 'assets', ['target_id'], unique=False)

    # Observations
    op.create_table(
        'observations',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('workspace_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('workspaces.id', ondelete='CASCADE'), nullable=False),
        sa.Column('assessment_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('assessments.id', ondelete='CASCADE'), nullable=False),
        sa.Column('asset_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('assets.id', ondelete='SET NULL'), nullable=True),
        sa.Column('observation_type', sa.String(length=128), nullable=False),
        sa.Column('subject_identifier', sa.String(length=512), nullable=False),
        sa.Column('domain_name', sa.String(length=255), nullable=True),
        sa.Column('ip_address', postgresql.INET(), nullable=True),
        sa.Column('service_port', sa.Integer(), nullable=True),
        sa.Column('provider_payload', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    )
    op.create_index(op.f('ix_observations_workspace_id'), 'observations', ['workspace_id'], unique=False)
    op.create_index(op.f('ix_observations_assessment_id'), 'observations', ['assessment_id'], unique=False)
    op.create_index(op.f('ix_observations_asset_id'), 'observations', ['asset_id'], unique=False)
    op.create_index(op.f('ix_observations_observation_type'), 'observations', ['observation_type'], unique=False)
    op.create_index(op.f('ix_observations_subject_identifier'), 'observations', ['subject_identifier'], unique=False)
    op.create_index(op.f('ix_observations_domain_name'), 'observations', ['domain_name'], unique=False)
    op.create_index(op.f('ix_observations_ip_address'), 'observations', ['ip_address'], unique=False)
    op.create_index(op.f('ix_observations_service_port'), 'observations', ['service_port'], unique=False)

    # Findings
    op.create_table(
        'findings',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('workspace_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('workspaces.id', ondelete='CASCADE'), nullable=False),
        sa.Column('assessment_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('assessments.id', ondelete='CASCADE'), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('severity', finding_severity_enum, nullable=False),
        sa.Column('status', finding_status_enum, nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    )
    op.create_index(op.f('ix_findings_workspace_id'), 'findings', ['workspace_id'], unique=False)
    op.create_index(op.f('ix_findings_assessment_id'), 'findings', ['assessment_id'], unique=False)
    op.create_index(op.f('ix_findings_title'), 'findings', ['title'], unique=False)
    op.create_index('ix_findings_workspace_severity', 'findings', ['workspace_id', 'severity'], unique=False)
    op.create_index('ix_findings_workspace_status', 'findings', ['workspace_id', 'status'], unique=False)

    # Evidence
    op.create_table(
        'evidence',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('workspace_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('workspaces.id', ondelete='CASCADE'), nullable=False),
        sa.Column('assessment_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('assessments.id', ondelete='CASCADE'), nullable=False),
        sa.Column('storage_location', sa.String(length=512), nullable=False),
        sa.Column('content_checksum', sa.String(length=64), nullable=True, comment='Cryptographic SHA256 checksum for integrity verification.'),
        sa.Column('content_type', sa.String(length=128), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    )
    op.create_index(op.f('ix_evidence_workspace_id'), 'evidence', ['workspace_id'], unique=False)
    op.create_index(op.f('ix_evidence_assessment_id'), 'evidence', ['assessment_id'], unique=False)
    op.create_index(op.f('ix_evidence_storage_location'), 'evidence', ['storage_location'], unique=False)
    op.create_index(op.f('ix_evidence_content_checksum'), 'evidence', ['content_checksum'], unique=False)

    # Reports
    op.create_table(
        'reports',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('workspace_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('workspaces.id', ondelete='CASCADE'), nullable=False),
        sa.Column('assessment_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('assessments.id', ondelete='CASCADE'), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('report_status', report_status_enum, nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    )
    op.create_index(op.f('ix_reports_workspace_id'), 'reports', ['workspace_id'], unique=False)
    op.create_index(op.f('ix_reports_assessment_id'), 'reports', ['assessment_id'], unique=False)
    op.create_index(op.f('ix_reports_title'), 'reports', ['title'], unique=False)
    op.create_index('ix_reports_workspace_status', 'reports', ['workspace_id', 'report_status'], unique=False)

    # 3. Association Tables
    # authorization_targets
    op.create_table(
        'authorization_targets',
        sa.Column('authorization_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('authorizations.id', ondelete='CASCADE'), primary_key=True),
        sa.Column('target_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('targets.id', ondelete='CASCADE'), primary_key=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    )

    # authorization_scopes
    op.create_table(
        'authorization_scopes',
        sa.Column('authorization_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('authorizations.id', ondelete='CASCADE'), primary_key=True),
        sa.Column('scope_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('scopes.id', ondelete='CASCADE'), primary_key=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    )

    # finding_observations
    op.create_table(
        'finding_observations',
        sa.Column('finding_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('findings.id', ondelete='CASCADE'), primary_key=True),
        sa.Column('observation_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('observations.id', ondelete='CASCADE'), primary_key=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    )

    # finding_evidence
    op.create_table(
        'finding_evidence',
        sa.Column('finding_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('findings.id', ondelete='CASCADE'), primary_key=True),
        sa.Column('evidence_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('evidence.id', ondelete='CASCADE'), primary_key=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    )


def downgrade() -> None:
    # Drop Association Tables
    op.drop_table('finding_evidence')
    op.drop_table('finding_observations')
    op.drop_table('authorization_scopes')
    op.drop_table('authorization_targets')

    # Drop Main Tables
    op.drop_table('reports')
    op.drop_table('evidence')
    op.drop_table('findings')
    op.drop_table('observations')
    op.drop_table('assets')
    op.drop_table('assessments')
    op.drop_table('scope_rules')
    op.drop_table('scopes')
    op.drop_table('authorizations')
    op.drop_table('targets')
    op.drop_table('workspaces')

    # Drop Enums using single module-level objects
    report_status_enum.drop(op.get_bind(), checkfirst=True)
    finding_status_enum.drop(op.get_bind(), checkfirst=True)
    finding_severity_enum.drop(op.get_bind(), checkfirst=True)
    asset_type_enum.drop(op.get_bind(), checkfirst=True)
    assessment_status_enum.drop(op.get_bind(), checkfirst=True)
    assessment_mode_enum.drop(op.get_bind(), checkfirst=True)
    scope_rule_category_enum.drop(op.get_bind(), checkfirst=True)
    scope_rule_action_enum.drop(op.get_bind(), checkfirst=True)
    authorization_status_enum.drop(op.get_bind(), checkfirst=True)
    target_category_enum.drop(op.get_bind(), checkfirst=True)

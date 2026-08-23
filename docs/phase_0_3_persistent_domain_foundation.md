# Phase 0.3: Persistent Domain Foundation Documentation

## 1. Purpose of Phase 0.3

The objective of **Phase 0.3** is to implement the relational persistent database schema for the **Mystic Security Platform** based on the frozen Phase 0.2 Core Domain Architecture. This phase introduces:

- PostgreSQL persistence layer via SQLAlchemy 2.x declarative models.
- Version-controlled schema migrations via Alembic.
- Core domain models for 10 primary persistent domain entities and 1 relational child entity.
- Relational association tables for multi-target authorization and finding traceability.
- PostgreSQL-native network types (`INET`, `CIDR`) and conservative, workspace-scoped index structures.
- Explicit foreign key deletion policies (`RESTRICT` for historical audit preservation, `SET NULL` for empirical asset retention).
- Strict Real-Data-Only guarantee (zero seed scripts, zero mock data, zero auto-populated application records).

---

## 2. Persistent Entities Implemented

The database schema implements **10 primary persistent domain entities** and **1 persistent relational child entity** as SQLAlchemy 2.x declarative models in `app/models/`:

### Primary Domain Entities (10)
1. **`Workspace`** (`workspaces`): Top-level organizational isolation boundary.
2. **`Target`** (`targets`): Empirical physical or logical subject intended for evaluation (Domain, IP, URL, Network Range, Application).
3. **`Authorization`** (`authorizations`): Independent Workspace operational consent record (`DRAFT`, `PENDING`, `ACTIVE`, `REVOKED`).
4. **`Scope`** (`scopes`): Workspace container for technical boundary rules.
5. **`Assessment`** (`assessments`): Central historical evaluation entity binding primary Target, Authorization, Scope, and JSONB Execution Snapshot.
6. **`Asset`** (`assets`): Verified empirical host, domain, IP, service, or application.
7. **`Observation`** (`observations`): Atomic empirical fact extracted from raw outputs (hybrid relational/JSONB model).
8. **`Finding`** (`findings`): Verified security conclusion / vulnerability (`CRITICAL`, `HIGH`, `MEDIUM`, `LOW`, `INFO`).
9. **`Evidence`** (`evidence`): Storage metadata pointer and SHA256 integrity checksum for raw logs and payloads.
10. **`Report`** (`reports`): Generated point-in-time export document metadata (`GENERATING`, `PUBLISHED`, `ARCHIVED`).

### Relational Child Entities (1)
11. **`ScopeRule`** (`scope_rules`): Relational child entity of `Scope` representing inclusion/exclusion rules (`INCLUDE` / `EXCLUDE`) matching domains, CIDRs, IPs, or patterns.

---

## 3. Entity Relationship & Primary Target Overview

```text
Workspace
├── Targets (1-to-N) ◄────── Association: authorization_targets ──────► Authorizations (1-to-N)
├── Scopes (1-to-N) ◄─────── Association: authorization_scopes ───────┘
│     └── ScopeRules (Child 1-to-N)
└── Assessments (1-to-N)
      ├── primary target_id (FK to targets.id — Root Context; RESTRICT deletion)
      ├── JSONB execution_snapshot (Target, Auth, Scope, Mode, Policy, Plan DAG)
      ├── Assets (1-to-N)
      │     └── Observations (1-to-N) ◄── Association: finding_observations ──┐
      ├── Findings (1-to-N) ──────────────────────────────────────────────────┤
      │     └── Evidence (1-to-N) ◄────── Association: finding_evidence ──────┘
      └── Reports (1-to-N)
```

---

## 4. Foreign Key Deletion Policies

Foreign key deletion policies were deliberately configured to prevent accidental destruction of historical security evaluation and audit records:

- **`RESTRICT` (Historical Audit Protection):**
  - `assessments.target_id` $\rightarrow$ `targets.id`: Restricts target deletion if referenced by an Assessment.
  - `assessments.authorization_id` $\rightarrow$ `authorizations.id`: Restricts deletion of operational consent records if referenced by an Assessment.
  - `assessments.scope_id` $\rightarrow$ `scopes.id`: Restricts deletion of technical scope boundary definitions if referenced by an Assessment.
- **`SET NULL` (Empirical Lineage Preservation):**
  - `assets.target_id` $\rightarrow$ `targets.id`: If a root target is unlinked, discovered empirical assets retain their historical existence with `target_id = NULL`.
  - `observations.asset_id` $\rightarrow$ `assets.id`: If an asset is deleted, raw atomic observations are preserved with `asset_id = NULL`.
- **`CASCADE` (Parent Container Cleanup):**
  - `workspace_id` FKs across all entities use `CASCADE` for multi-tenant workspace deletion.
  - `scope_rules.scope_id` uses `CASCADE` (child rules belong strictly to parent Scope).
  - Assessment child entities (`assets`, `observations`, `findings`, `evidence`, `reports`) use `CASCADE` when an Assessment container is explicitly deleted.
  - Association tables (`authorization_targets`, `authorization_scopes`, `finding_observations`, `finding_evidence`) use `CASCADE`.

---

## 5. Data Integrity & Uniqueness Constraints

The schema enforces strict relational uniqueness to prevent duplicate records per workspace and assessment:

1. `workspaces`: `UniqueConstraint("name", name="uq_workspaces_name")`
2. `targets`: `UniqueConstraint("workspace_id", "identifier", name="uq_targets_workspace_identifier")`
3. `authorizations`: `UniqueConstraint("workspace_id", "reference_code", name="uq_authorizations_workspace_refcode")`
4. `scopes`: `UniqueConstraint("workspace_id", "name", name="uq_scopes_workspace_name")`
5. `assets`: `UniqueConstraint("assessment_id", "identifier", name="uq_assets_assessment_identifier")`
6. `authorizations`: `CheckConstraint("valid_from <= valid_until", name="check_valid_authorization_dates")`

---

## 6. Index Audit & Workspace-Scoped Index Strategy

### Index Audit Strategy
- **Primary Key Indexes:** Redundant `index=True` declarations on primary key `id` columns were removed across all models because PostgreSQL automatically builds unique B-tree indexes on `PRIMARY KEY (id)`.
- **Uniqueness Constraint Indexes:** Standalone indexes on `workspace.name`, `target.identifier`, `authorization.reference_code`, `scope.name`, and `asset.identifier` were removed because PostgreSQL automatically creates unique composite B-tree indexes when creating `UniqueConstraint`s!
- **Standalone Low-Cardinality Enum Indexes:** Removed standalone single-column indexes on low-cardinality enum columns (`target_category`, `persisted_status`, `rule_action`, `rule_category`, `assessment_mode`, `status`, `asset_type`, `severity`, `report_status`).

### Retained & Composite Workspace Indexes
- **Foreign Key Indexes:** Retained explicit B-tree indexes on foreign keys (`workspace_id`, `target_id`, `authorization_id`, `scope_id`, `assessment_id`, `asset_id`) to accelerate relational join queries.
- **Workspace Validity Composite Index:** `Index("ix_authorizations_validity", "workspace_id", "persisted_status", "valid_from", "valid_until")` on `authorizations` for dynamic effective validity query evaluation.
- **Workspace Assessment Status Composite Index:** `Index("ix_assessments_workspace_status", "workspace_id", "status")` on `assessments` for workspace dashboard monitoring.
- **Workspace Finding Severity/Status Composite Indexes:** `Index("ix_findings_workspace_severity", "workspace_id", "severity")` and `Index("ix_findings_workspace_status", "workspace_id", "status")` on `findings`.
- **Workspace Report Status Composite Index:** `Index("ix_reports_workspace_status", "workspace_id", "report_status")` on `reports`.

---

## 7. ScopeStatus Removal & Assessment Minimization

- **ScopeStatus:** Removed from schema. Runtime scope evaluation results (`IN_SCOPE` / `OUT_OF_SCOPE`) belong to the Scope Engine in future execution phases.
- **AssessmentStatus:** Minimized to 7 core persisted lifecycle states (`DRAFT`, `READY`, `QUEUED`, `RUNNING`, `CANCELLED`, `COMPLETED`, `FAILED`).

---

## 8. Model-to-Migration 1-to-1 Consistency

Field-by-field verification confirms 100% structural alignment between SQLAlchemy models in `app/models/` and Alembic migration `001_initial_domain_schema.py`:
- All table names, column names, PostgreSQL types (`UUID`, `INET`, `CIDR`, `JSONB`), nullable flags, primary keys, foreign keys with explicit deletion policies (`RESTRICT`/`SET NULL`/`CASCADE`), unique constraints, check constraints, enum names/values, and indexes match identically.

---

## 9. Real-Data-Only Guarantee

**Zero application data, seed records, sample targets, mock findings, or default users were created.**

Alembic migration `001_initial_domain_schema.py` contains **pure schema DDL statements** (`op.create_table`, `op.create_index`, `op.create_enum`). When run by the operator, the database will contain complete tables and zero domain rows.

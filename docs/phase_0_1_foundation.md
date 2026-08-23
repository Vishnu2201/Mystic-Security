# Phase 0.1 Project Foundation Document

## 1. Purpose

The objective of **Phase 0.1** is to establish a clean, minimal, runnable project foundation for the **Mystic Security Platform**. This foundation establishes:

- Clear boundary separation between frontend, backend, infrastructure, and documentation.
- Production-grade build and environment configuration across React/TypeScript and FastAPI.
- Development container infrastructure boundaries via Docker Compose.
- Strict enforcement of project invariants (Real-Data-Only policy, capability-driven architectural framework).

---

## 2. Implemented Boundaries

### Frontend Boundary (`/frontend`)
- **Framework:** React 18, TypeScript, Vite.
- **Styling:** Tailwind CSS v3 with global dark mode styling.
- **Components:** Clean application shell (`Layout`, `Header`, `Footer`), system status card, and clean empty state presentation.
- **Strict Invariant:** Zero demo targets, mock findings, sample cards, or fake cybersecurity dashboard statistics.

### Backend Boundary (`/backend`)
- **Framework:** FastAPI, Python 3.12, Pydantic v2.
- **Configuration:** Environment settings management via `pydantic-settings`.
- **API Routing:** Clean router structure (`/api/v1`) exposing a truthful `/api/v1/health` status endpoint.
- **CORS Middleware:** Configured cross-origin support for Vite development server.

### Infrastructure Boundary (`/infrastructure` & `/docker-compose.yml`)
- **Orchestration:** Minimal local Docker Compose manifest provisioning `db` (PostgreSQL 16), `backend`, and `frontend`.
- **Isolation:** Explicit separation of web and database containers; no direct container socket access exposed to web API containers.

---

## 3. Intentionally Excluded Functionality (Postponed to Later Phases)

The following components were **explicitly NOT implemented** in Phase 0.1 to avoid premature implementation and architectural clutter:

- **Authentication & User Management:** No JWT, OAuth, or RBAC logic.
- **Multi-Tenancy Workspaces:** No workspace isolation models.
- **Domain Data Models & Database Migrations:** No ORM models, tables, or Alembic migrations.
- **Target, Authorization & Scope Engines:** No target registration, authorization date checks, or scope rule evaluators.
- **Assessment Planner & Execution Engine:** No DAG generation, strategy maps, or capability runs.
- **Background Task Workers:** No Redis brokers, Dramatiq workers, or execution queues.
- **Tool Execution Sandboxes:** No ephemeral Docker container runners or tool adapters.
- **Evidence Storage & Normalizer:** No MinIO/S3 integrations or observation parsers.
- **Vulnerability Findings & Reports:** No finding definitions or report generators.
- **AI Integrations & MCP Providers:** No LLM or Model Context Protocol connectors.

---

## 4. Next Expected Phase (Phase 1)

The next step in the platform roadmap is **Phase 1: Core Foundation & Data Layer Setup**:

1. Implement core database models (`Workspace`, `User`, `Target`, `Scope`, `ScopeRule`, `Authorization`).
2. Configure SQLAlchemy v2 async engine and Alembic migrations.
3. Build the Operational Authorization Lifecycle state machine (`Draft`, `Pending`, `Active`, `Expired`, `Revoked`).
4. Build the Scope Gatekeeper engine for validating seed targets and discovered hosts.

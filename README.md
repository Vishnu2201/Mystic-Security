# Mystic Security Platform

A unified, long-term cybersecurity assessment platform for authorized security testing, vulnerability assessment, penetration testing, internal infrastructure testing, labs/CTF environments, and authorized bug bounty programs.

---

## Architectural Philosophy & Core Principles

Mystic Security Platform is strictly **capability-driven**. Unlike legacy platforms that present users with a dashboard of discrete tool trigger buttons (e.g., "Run Nmap", "Run Subfinder"), Mystic Security abstracts security binaries, external APIs, and tools into implementation providers hidden behind high-level capability contracts (e.g., `DNS Resolution`, `Network Discovery`).

### Key Invariants

1. **Capability-Driven Abstraction:** Users define assessment goals, targets, authorization limits, and assessment modes (`FAST`, `BALANCED`, `THOROUGH`, `CUSTOM`). The platform internally manages capability execution graphs and provider selection.
2. **Absolute Real Data Only:** The platform contains zero demo targets, mock findings, sample vulnerabilities, seeded database records, or fake dashboard statistics. Empty database states render clean, informative empty UI states.
3. **Operational Authorization & First-Class Scope:** Assessments require an explicit, active `Authorization` record within a valid date window. All discovered targets pass through a Scope Gatekeeper before downstream active capabilities execute.
4. **Immutable Raw Evidence & Provenance:** Tool output streams (stdout, stderr, JSON payloads) are stored immutably with cryptographic checksums and retention policies. Derived assets and findings maintain full lineage to their originating raw evidence.
5. **Isolated Container Runtime:** The core API and UI have zero direct access to the container execution engine. Container spawns are handled exclusively by isolated background execution workers.

---

## Current Project Status: Phase 0.3 Persistent Domain Foundation

> [!NOTE]
> **Current Status: Phase 0.3 Persistent Domain Foundation Implemented.**
> Phase 0.1 established the application foundation shell, FastAPI health endpoint (`/api/v1/health`), React layout, and local Docker Compose infrastructure.
> Phase 0.2 specified the formal conceptual domain architecture (`docs/phase_0_2_core_domain_architecture.md`).
> Phase 0.3 implements the SQLAlchemy 2.x declarative models, Alembic schema migrations (`001_initial_domain_schema.py`), and PostgreSQL persistence layer (`docs/phase_0_3_persistent_domain_foundation.md`).
> **Zero seed data, sample targets, mock findings, or default records exist. The migrated database contains pure schema DDL and zero domain records.**

---

## Technology Stack

* **Frontend:** React 18, TypeScript, Vite, Tailwind CSS
* **Backend:** Python 3.12, FastAPI, Pydantic v2, SQLAlchemy 2.x, Alembic
* **Database:** PostgreSQL 16 (Native `INET`/`CIDR` types, `JSONB` execution snapshots, `UUID` primary keys)
* **Container Infrastructure:** Docker & Docker Compose

---

## Repository Structure

```text
Mystic Security/
│
├── backend/                  # FastAPI Application
│   ├── app/
│   │   ├── api/              # API Routing & Endpoints
│   │   │   └── endpoints/    # Health / Status routes
│   │   ├── core/             # Configuration & Settings
│   │   └── main.py           # Application Entry Point
│   ├── Dockerfile
│   └── requirements.txt
│
├── frontend/                 # React + TypeScript + Vite Application
│   ├── src/
│   │   ├── components/       # Layout & UI Components
│   │   ├── App.tsx           # Main Application Shell
│   │   ├── main.tsx          # React DOM Mount Point
│   │   └── index.css         # Global Styles & Tailwind Directives
│   ├── index.html
│   ├── Dockerfile
│   ├── package.json
│   ├── tailwind.config.js
│   └── vite.config.ts
│
├── infrastructure/           # Infrastructure & Container Boundary Specs
│   └── README.md
│
├── docs/                     # Project Architecture Documentation
│   └── phase_0_1_foundation.md
│
├── .env.example              # Environment Configuration Template
├── .gitignore                # Git Ignore Rules
├── docker-compose.yml        # Development Docker Compose Manifest
└── README.md                 # Project Overview & Setup Instructions
```

---

## Getting Started (Local Development)

### Option 1: Direct Local Execution

#### Backend Setup
```bash
cd backend
python -m venv venv
# On Windows:
.\venv\Scripts\activate
# On Linux/macOS:
# source venv/bin/activate

pip install -r requirements.txt
python -m uvicorn app.main:app --reload --port 8000
```
Verify backend health: `http://localhost:8000/api/v1/health`

#### Frontend Setup
```bash
cd frontend
npm install
npm run dev
```
Open application shell: `http://localhost:5173`

---

### Option 2: Docker Compose Setup

```bash
# Copy environment configuration
cp .env.example .env

# Build and start development containers
docker compose up --build
```

* **Frontend:** `http://localhost:5173`
* **Backend API Health:** `http://localhost:8000/api/v1/health`

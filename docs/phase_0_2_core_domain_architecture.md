# Phase 0.2: Core Domain Architecture Specification

## 1. Phase Objective

The objective of **Phase 0.2** is to specify the formal conceptual domain architecture for the **Mystic Security Platform**. This document establishes:

- Core domain entities, value objects, and configuration concepts.
- Explicit responsibilities and architectural boundaries for each domain concept.
- The revised domain relationship model connecting Workspaces, Targets, Authorizations, Scopes, Assessments, Capabilities, Assets, Observations, Findings, Evidence, and Reports.
- Minimal state lifecycle models for all dynamic entities, distinguishing persisted status from dynamic effective validity.
- Historical integrity and snapshotting strategies to guarantee auditability and execution provenance.
- Critical backend invariants that must be enforced by application logic.
- Explicit boundaries separating conceptual architecture from future implementation phases.

---

## 2. Core Domain Concepts & Responsibilities

### 2.1 Workspace
- **Purpose:** Primary boundary for organizational data isolation and security operations.
- **Responsibilities:**
  - Conceptually groups related Targets, Authorizations, Scopes, Assessments, Assets, Findings, Evidence, and Reports.
  - Serves as the top-level security boundary for future access control and role-based permissions.
- **Out of Scope for Phase 0.2:** Multi-tenant user routing, organization management, or JWT tenant isolation logic.

### 2.2 Target
- **Purpose:** Represents an empirical physical or logical subject intended for security evaluation.
- **Categories:** Domain Name (e.g., `example.com`), IP Address (e.g., `192.168.1.1`), URL (e.g., `https://api.example.com`), Network Range / CIDR (e.g., `10.0.0.0/24`), or Application identifier.
- **Responsibilities:**
  - Maintains canonical target identity, category classification, and validation rules.
  - Normalizes target identifiers (e.g., lowercase domains, standard IPv4/IPv6 notation).
- **Critical Architectural Boundary:** A Target represents *what exists*, **NOT** permission to test it. The existence of a Target never implies authorization.

### 2.3 Authorization (Workspace-Level Concept & Expiration Semantics)
- **Purpose:** Serves as an independent operational consent record granting permission to perform security testing.
- **Scope of Coverage:** Workspace-level concept that may govern multiple Targets, domain collections, subdomains, IP ranges, applications, or broader scope definitions.
- **Persisted Lifecycle Status:**
  - `Draft`: Initial record creation; pending review.
  - `Pending`: Awaiting owner/operator sign-off.
  - `Active`: Explicitly approved for execution.
  - `Revoked`: Explicitly invalidated prior to date expiration.
- **Effective Validity Model (Dynamic Runtime Evaluation):**
  Expiration is evaluated dynamically from timestamp boundaries (`valid_from`, `valid_until`) rather than mutating database records via background cron workers.
  - `Draft`: Persisted status is `Draft`.
  - `Pending`: Persisted status is `Pending`.
  - `Revoked`: Persisted status is `Revoked`.
  - `Not Yet Valid`: Persisted status is `Active`, but $t_{\text{now}} < \text{valid\_from}$.
  - `Valid`: Persisted status is `Active`, and $\text{valid\_from} \le t_{\text{now}} \le \text{valid\_until}$.
  - `Expired`: Persisted status is `Active`, but $t_{\text{now}} > \text{valid\_until}$.
- **Execution Invariant:** Execution is permitted ONLY when persisted status is `Active`, authorization is not `Revoked`, and current time is within `valid_from` $\le t_{\text{now}} \le$ `valid_until`.

### 2.4 Scope
- **Purpose:** Defines the precise technical boundaries of allowed and forbidden security testing activity.
- **Responsibilities:**
  - Maintains explicit inclusion rules (e.g., allowed subdomains, allowed IP ranges, allowed port ranges).
  - Maintains explicit exclusion rules (e.g., forbidden hostnames, excluded paths, production out-of-bounds IPs).
  - Evaluated by the backend Scope Engine before execution and after asset discovery.

### 2.5 Out-of-Scope Discovery Handling
- **Strict Boundary:** A discovered candidate host/IP MUST undergo scope evaluation before becoming an actively assessed Asset.
- **Out-of-Scope Candidate Rules:**
  1. MUST NOT receive active security testing.
  2. MUST NOT become a normal assessment `Asset` by default.
  3. MUST NOT generate `Finding`s.
  4. Retains only minimal execution audit metadata when necessary for execution traceability (e.g., audit log entry of skipped candidate targets).
  5. Otherwise may be discarded according to storage retention policies.

### 2.6 Assessment
- **Purpose:** Represents an instance of an authorized security evaluation executed against a Target under an approved Scope.
- **Responsibilities:**
  - Tracks top-level execution intent, requested Assessment Mode (`FAST`, `BALANCED`, `THOROUGH`, `CUSTOM`), and overall state lifecycle.
  - Binds together the Target, Authorization, Scope, and Execution Snapshot context for a specific run.

### 2.7 Assessment Plan vs. Assessment Mode
- **Assessment Mode:** Represents the user's high-level execution intent selected at queue time (`FAST`, `BALANCED`, `THOROUGH`, `CUSTOM`).
- **Assessment Plan:** Represents the concrete, dependency-aware capability strategy DAG generated for that Assessment execution.
- **Architecture & Persistence Decision:** Option A — `AssessmentPlan` is conceptually an **immutable execution graph snapshot embedded within an Assessment** (stored as a structured JSON attribute of the Assessment's execution snapshot context alongside the Assessment Mode snapshot). Both are preserved independently for auditability.

### 2.8 Capability
- **Purpose:** Defines a stable, tool-agnostic security evaluation objective (e.g., `DNS Resolution`, `Port Discovery`, `HTTP Discovery`, `TLS Analysis`, `Technology Detection`).
- **Responsibilities:**
  - Defines input contracts, expected output observation types, and standard execution requirements.
  - Acts as an abstract domain interface. Underlying security tools (CLI binaries, Python libraries, APIs) are pluggable implementation details.

### 2.9 Capability Run
- **Purpose:** Represents an individual runtime execution instance of a single Capability node within an Assessment Plan.
- **Responsibilities:**
  - Tracks execution status (`Pending`, `Queued`, `Running`, `Succeeded`, `Failed`, `Skipped`, `Cancelled`), timestamps, and error context.
  - Preserves partial failure states to ensure non-dependent plan branches complete gracefully.

### 2.10 Asset
- **Purpose:** Represents a verified empirical host, domain, IP address, service, or application identified during authorized testing.
- **Responsibilities:**
  - Maintains empirical inventory derived strictly from real execution outputs or explicit user specification.
  - Establishes relationships (e.g., Domain `example.com` `RESOLVED_TO` IP `93.184.216.34`).
- **Strict Invariant:** Assets must originate from empirical evidence or real user input. Fake or pre-seeded discovery records are strictly forbidden.

### 2.11 Observation
- **Purpose:** Represents an atomic, factual piece of empirical data extracted from raw execution outputs.
- **Responsibilities:**
  - Stores structured factual attributes (e.g., open port number, DNS record value, HTTP response code).
  - Uses a hybrid data pattern (indexed relational columns for queryable attributes + provider payload for raw details).
- **Critical Architectural Boundary:** An Observation is a neutral empirical fact. It is **NOT** automatically a vulnerability or finding.

### 2.12 Finding & Traceability
- **Purpose:** Represents a verified security-relevant conclusion (vulnerability, misconfiguration, weakness) derived from assessment data.
- **Traceability Boundary:**
  - A Finding MUST be traceable to actual assessment-produced information.
  - Supported by one or more `Observation`s and/or `Evidence` references as appropriate to the evidence type.

### 2.13 Evidence
- **Purpose:** Represents the immutable supporting material proving the existence of an Observation or Finding.
- **Responsibilities:**
  - Links to raw execution output logs stored in object storage.
  - Retains cryptographic SHA256 integrity checksums, timestamps, and tool execution identifiers.

### 2.14 Report
- **Purpose:** Represents an exported, point-in-time summary document derived from an Assessment's verified Assets and Findings.

---

## 3. Domain Relationship Model

```text
Workspace
├── Targets
├── Authorizations (Independent Workspace-level entity)
├── Scopes
└── Assessments
      ├── Immutable Execution Context (Snapshot)
      │     ├── Target reference/snapshot
      │     ├── Authorization reference/snapshot
      │     ├── Scope snapshot
      │     ├── Assessment Mode snapshot
      │     ├── Restrictions/Execution Policy snapshot
      │     └── Assessment Plan DAG snapshot
      │
      ├── Capability Runs
      ├── Assets
      │     └── Observations
      ├── Findings
      │     └── Evidence / supporting references
      └── Reports
```

---

## 4. Concept Classification

| Concept | Classification | Architectural Purpose |
| :--- | :--- | :--- |
| **Workspace** | Persistent Entity Candidate | Multi-tenancy isolation boundary. |
| **Target** | Persistent Entity Candidate | Subject of security testing. |
| **Authorization** | Persistent Entity Candidate | Independent Workspace consent record (`Draft`, `Pending`, `Active`, `Revoked`). |
| **Scope** | Persistent Entity Candidate | Container for technical boundaries. |
| **ScopeRule** | Value / Configuration Object | Individual inclusion/exclusion match specification. |
| **Assessment** | Persistent Entity Candidate | Top-level evaluation instance. |
| **AssessmentMode** | Enumerated Value Concept | Strategy intensity (`FAST`, `BALANCED`, `THOROUGH`, `CUSTOM`). |
| **AssessmentPlan** | Embedded Execution Snapshot | Immutable JSON DAG snapshot stored inside Assessment. |
| **ExecutionSnapshot** | Embedded Execution Snapshot | Frozen context (Target, Auth, Scope, Mode, Policy, Plan). |
| **Capability** | Domain Registry Contract | Abstract functional contract (tool-agnostic). |
| **CapabilityRun** | Execution Tracking Concept | Runtime state entity tracking a single plan node. |
| **ExecutionPolicy** | Configuration Object | Resource limits, timeouts, and network boundary rules. |
| **Asset** | Persistent Entity Candidate | Discovered empirical host, IP, or service. |
| **Observation** | Persistent Entity Candidate | Parsed atomic fact (hybrid relational/JSONB model). |
| **Finding** | Persistent Entity Candidate | Derived security conclusion / vulnerability. |
| **Evidence** | Persistent Entity Candidate | Immutable link to raw log payload and SHA256 hash. |
| **Report** | Persistent Entity Candidate | Generated assessment export document. |

---

## 5. Lifecycle & State Models

```text
[ TARGET LIFECYCLE ]
Draft ──> Active ──> Archived

[ AUTHORIZATION PERSISTED LIFECYCLE ]
Draft ──> Pending ──> Active ──> Revoked

[ ASSESSMENT LIFECYCLE ]
Draft ──> Planning ──> Ready ──> Queued ──> Running ──> [ Cancelling ──> Cancelled ]
                                              │
                                              ├──> Completed
                                              ├──> Completed With Warnings
                                              └──> Failed

[ CAPABILITY RUN LIFECYCLE ]
Pending ──> Queued ──> Running ──> [ Succeeded | Failed | Skipped | Cancelled ]

[ FINDING LIFECYCLE ]
Unverified ──> Confirmed ──> [ False Positive | Remediated | Accepted Risk ]

[ REPORT LIFECYCLE ]
Generating ──> Published ──> Archived
```

### Authorization Effective Validity Model
Rather than running background worker cron jobs to mutate database rows when dates expire, the backend evaluates **Effective Validity** dynamically at runtime:

$$\text{EffectiveValidity} = \begin{cases} 
\text{Draft} & \text{if } \text{status} = \text{Draft} \\
\text{Pending} & \text{if } \text{status} = \text{Pending} \\
\text{Revoked} & \text{if } \text{status} = \text{Revoked} \\
\text{Not Yet Valid} & \text{if } \text{status} = \text{Active} \land t_{\text{now}} < \text{valid\_from} \\
\text{Valid} & \text{if } \text{status} = \text{Active} \land \text{valid\_from} \le t_{\text{now}} \le \text{valid\_until} \\
\text{Expired} & \text{if } \text{status} = \text{Active} \land t_{\text{now}} > \text{valid\_until}
\end{cases}$$

To execute an Assessment, $\text{EffectiveValidity}$ MUST resolve to **`Valid`**.

---

## 6. Historical Integrity & Assessment Execution Snapshot Strategy

When an Assessment transitions to `Ready` or `Queued` for execution, the backend freezes the execution context into an **Assessment Execution Snapshot**:

```json
{
  "execution_snapshot_version": "<STRING>",
  "snapshot_timestamp": "<TIMESTAMP>",
  "target_snapshot": {
    "target_id": "<UUID>",
    "identifier": "<STRING>",
    "target_category": "<ENUM>"
  },
  "authorization_snapshot": {
    "authorization_id": "<UUID>",
    "reference_code": "<STRING>",
    "persisted_status_at_queue": "<ENUM>",
    "valid_until": "<TIMESTAMP>"
  },
  "scope_snapshot": {
    "scope_id": "<UUID>",
    "inclusion_rules": "<ARRAY>",
    "exclusion_rules": "<ARRAY>"
  },
  "assessment_mode_snapshot": "<ENUM>",
  "execution_policy_snapshot": {
    "max_timeout_seconds": "<INTEGER>",
    "allowed_ports": "<ARRAY>"
  },
  "assessment_plan_dag_snapshot": {
    "plan_nodes": "<ARRAY_OF_OBJECTS>"
  }
}
```

### Snapshot Guarantees
* **Independent Evolution:** Current Workspace settings, Target descriptions, or Authorization records may continue evolving independently over time without altering historical Assessment execution snapshots.
* **Preservation of Intent vs. Strategy:** The Assessment Mode snapshot preserves original user intent (`FAST`), while the Assessment Plan snapshot preserves the generated capability strategy graph (`DNS_RESOLUTION`). Both are preserved independently.
* **Audit Integrity:** Historical assessments remain fully auditable and reproducible even if capability definitions, tool providers, or strategies change in future platform versions.

---

## 7. Critical Backend Invariants

The backend application logic must strictly enforce the following invariants:

1. **Invariant 1: Authorization Gate**
   An Assessment cannot execute unless Authorization persisted status is `Active`, not `Revoked`, and $\text{valid\_from} \le t_{\text{now}} \le \text{valid\_until}$ (Effective Validity == `Valid`).
2. **Invariant 2: Scope Gatekeeper & Out-of-Scope Exclusion**
   Discovered candidates must pass Scope evaluation before becoming active `Asset`s. Out-of-scope candidates are strictly excluded from active testing, generated Findings, and default Asset lists.
3. **Invariant 3: Capability Abstraction Boundary**
   The public API must never accept raw binary execution commands (e.g., `/api/run-nmap`). API requests specify high-level Assessment Modes or Capabilities.
4. **Invariant 4: Evidence Traceability**
   Every Finding must be traceable to actual assessment-produced Observations and/or Evidence references. Unbacked findings are forbidden.
5. **Invariant 5: Absolute Real-Data-Only Rule**
   Database queries and UI components must never return fake targets, mock vulnerabilities, or seeded metrics. Empty states must be returned when empirical data is absent.
6. **Invariant 6: Execution Runtime Segregation**
   The web API process must have zero direct access to container runtime sockets. Execution dispatch occurs asynchronously via task queues to dedicated execution workers.

---

## 8. Future Implementation Boundaries & Phase Mapping

- **Phase 0.1 (Complete):** Foundation layout, FastAPI health endpoint (`/api/v1/health`), React shell, Docker Compose.
- **Phase 0.2 (Complete - Current):** Core Domain Architecture specification & conceptual design (documentation only).
- **Phase 0.3:** Database Schema & Core Domain Model Implementation (SQLAlchemy v2 models, Pydantic schemas, Alembic migrations for Target, Scope, Authorization).
- **Phase 1:** Operational Authorization Lifecycle & Scope Gatekeeper Engine logic.
- **Phase 2:** Asynchronous Worker Queue (Redis + Dramatiq) & Ephemeral Container Execution Runner.
- **Phase 3:** MVP Vertical Slice — End-to-End DNS Resolution Capability Execution with Real Asset Graphing.
- **Phase 4:** Strategy Expansion & Vulnerability Findings Engine.
- **Phase 5:** Advanced Capabilities, MCP Provider Adapters & AI Analysis.

---

## 9. Explicitly Deferred Components

The following components are **explicitly postponed** and must **NOT** be created or implemented during Phase 0.2:

- SQLAlchemy ORM models or Alembic database migrations
- Database tables or PostgreSQL schema creation
- FastAPI API endpoints (beyond existing Phase 0.1 health route)
- React pages, forms, or navigation components
- Redis brokers, Dramatiq/Celery workers, or task queues
- Ephemeral Docker execution runners or tool binary containers
- Security tools or parser scripts
- MinIO/S3 file upload integrations
- PDF/Markdown report generators
- Demo data, sample targets, mock vulnerabilities, or seed scripts

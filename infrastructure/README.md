# Infrastructure Specifications & Boundaries

This directory maintains infrastructure specifications, environment definitions, and container boundary configurations for the Mystic Security Platform.

---

## Current Setup (Phase 0.1 Foundation)

In **Phase 0.1**, local development infrastructure is defined via `docker-compose.yml` in the project root:

- **`db`**: PostgreSQL 16 Alpine container (Database server boundary).
- **`backend`**: FastAPI application container.
- **`frontend`**: React + Vite application container.

---

## Architectural Container Boundaries (Future Phases)

As detailed in Architecture Blueprint v1.1, future infrastructure components will follow strict isolation rules:

1. **Platform Network (`platform-internal-net`):** Connects API, Database, Task Broker (Redis), and Evidence Storage (MinIO).
2. **Execution Worker Boundary:** Only dedicated execution runner workers will have access to the host Docker engine socket API. The FastAPI backend container will have **zero direct access** to Docker sockets.
3. **Tool Execution Network (`tool-exec-isolated-net`):** Ephemeral security tool containers spawned by workers will execute on a sandboxed network with no route to internal databases.

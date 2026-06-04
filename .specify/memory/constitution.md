<!--
SYNC IMPACT REPORT
==================
Version change  : none → 1.0.0 (initial ratification)
Modified        : n/a — first-ever constitution for this project
Added sections  :
  • Core Principles (I–X covering all ten mandated governance areas)
  • Technical Stack & Canonical APIs
  • Local Development Standards
  • Governance
Templates updated:
  • .specify/templates/plan-template.md  ✅ — Constitution Check gates updated
  • .specify/templates/spec-template.md  ✅ — constraint/scope notes aligned
  • .specify/templates/tasks-template.md ✅ — task categories reflect polling + AI boundary work
Deferred TODOs  :
  • None — all placeholders resolved from source-of-truth API docs
Source documents locked as authoritative:
  • api/Hotel-Search-doc.md
  • api/hotel-search-flow.md
  • architecture/ai-orchestration.md
-->

# NexTrip AI Constitution

## Core Principles

### I. Existing Backend APIs Are the Immutable Source of Truth

The Spring Boot wrapper layer (base URL `https://travelonedev-services.thomascook.in/`) is
the canonical, authoritative implementation of all hotel business logic. The following APIs
MUST NOT be re-implemented, duplicated, or replaced by any layer of this project:

| Capability | Endpoint |
|---|---|
| Token generation | `POST .../authenticationserver/authenticationService/generateToken` |
| Auto suggest | `POST /api/v1/wrapper/landing/fetchAutoSuggest` |
| Hotel search | `POST /api/v1/wrapper/hotels/search` |
| Background process status | `POST /api/v1/wrapper/hotels/backgroundProcessStatus` |
| Search by poll | `POST /api/v1/wrapper/hotels/search-by-poll` |
| Hotel details | `POST /api/v1/wrapper/room/getHotelDetails` |
| Room details | `POST /api/v1/wrapper/room/getRoomDetails` |

**Non-negotiable rules**:
- New code MUST call these APIs exactly as documented — no invented endpoints, no wrapper
  deviations, no DTO field additions or removals.
- The `correlationId + payload` envelope shape for requests MUST be preserved on every call.
- The `{ success, status, message, capability, correlationId, payload }` envelope shape for
  responses MUST be consumed as-is; callers MUST NOT re-shape or alias top-level fields.
- Any new feature that appears to require a backend change MUST be raised as a backend ticket
  first; the frontend and AI layer MUST NOT work around absent APIs with client-side
  reimplementations.

### II. AI Layer Orchestrates APIs — It Does Not Contain Business Logic

The FastAPI / LangGraph / OpenAI SDK layer is a pure orchestration boundary. Its only
permitted responsibilities are:

- Conversational understanding and search-intent extraction.
- Sequencing API calls in the correct order (AutoSuggest → Search → Poll loop → Details).
- Managing the polling lifecycle (polling triggers, status checks, termination).
- Summarising hotel results for conversational display.
- Maintaining per-session conversational state via Redis.
- Streaming incremental updates to the frontend via SSE.

The AI layer MUST NOT:
- Execute any pricing, availability, or booking logic.
- Read from or write to the MySQL database directly.
- Expose any endpoint that bypasses the Spring Boot wrapper layer.
- Invent or cache API data outside of the Redis conversational memory store.
- Call the Spring Boot APIs on behalf of the user with modified or fabricated payloads.

Violation of this boundary is a constitution breach and MUST block code review approval.

### III. Polling Architecture Is Non-Negotiable (NON-NEGOTIABLE)

Hotel search results are delivered asynchronously via a polling flow. This architecture MUST
be preserved in all implementations — it is dictated by the upstream vendor system.

**Mandatory lifecycle sequence**:
```
1. AutoSuggest  →  resolve destination identifiers
2. Search API   →  obtain { searchKey, cacheKey, autoSuggestId }
3. Background Process Status (loop)  →  poll until inProgress === false
4. Search By Poll  →  fetch incremental hotel pages
5. Frontend  →  progressively render results while polling continues
```

**Polling rules**:
- `searchKey`, `cacheKey`, and `autoSuggestId` are mandatory lifecycle identifiers. Any
  feature that touches the search flow MUST carry all three through every step.
- The AI layer MUST drive the polling loop; the frontend MUST NOT poll the backend Spring
  Boot APIs directly.
- Polling MUST terminate on: `inProgress === false`, a configurable timeout threshold
  (default: 60 s), or an unrecoverable downstream error.
- Frontend MUST support progressive rendering: hotels already fetched MUST be displayed
  before the poll loop completes.
- Polling state (searchKey, cacheKey, autoSuggestId, poll iteration count, status) MUST be
  persisted in Redis for the duration of the session.

### IV. Token Lifecycle Must Be Fully Automated

All Spring Boot APIs require a valid Bearer token obtained from the Token API. Token
management MUST be handled transparently by the AI orchestration layer (or a shared HTTP
client module) — it MUST never be the caller's responsibility to manage token state.

**Token refresh rules**:
- On application startup, a token MUST be eagerly fetched and stored in Redis with a TTL
  aligned to the upstream token expiry.
- On any API response that signals token expiry (e.g. `"token expired"` message or HTTP 401),
  the system MUST: (1) silently call the Token API to regenerate, (2) retry the failed
  request exactly once with the new token.
- If the retry also fails, the error MUST be propagated to the caller — no further retries.
- Token credentials (`moduleID`, `userName`, `password`) MUST be stored in environment
  variables, never committed to source code.
- A single shared token refresh module MUST be used across all API calls; duplicating token
  logic in individual services is prohibited.

### V. DTO Contracts Are Frozen — No Client-Side Mutations

Every request and response DTO documented in `api/Hotel-Search-doc.md` is the canonical,
versioned contract. These contracts are owned by the Spring Boot layer.

**Rules**:
- Request DTOs MUST be sent with exactly the fields documented — no extra fields, no omitted
  optional fields that have semantic meaning.
- Response DTOs MUST be consumed as-is. TypeScript interfaces on the frontend and Pydantic
  models in the AI layer MUST mirror the documented shapes exactly.
- Pydantic models (AI layer) and TypeScript types (frontend) MUST be updated in the same
  commit as any upstream contract change — drift between layers is a constitution violation.
- `correlationId` MUST be generated per-request using a UUID v4 and MUST be logged alongside
  every API call for traceability.
- The `capability` field in responses MUST be used for routing/handling logic; MUST NOT be
  ignored or hard-coded by feature code.

### VI. Persistence Is Scoped to Search History and Session State Only

MySQL (migrated by Flyway) stores only what cannot be held in Redis or the upstream vendor
system. The persistence scope for MVP is strictly:

- **search_history**: Logs of user search requests (destination, dates, rooms, timestamp,
  session ID) for auditability and future personalisation.
- **session_metadata**: Optional lightweight session bookkeeping if Redis TTL is insufficient.

**Rules**:
- The AI layer MUST write search history asynchronously — never blocking the search or poll
  flow.
- All schema changes MUST go through Flyway versioned migrations; no ad-hoc `ALTER TABLE`
  or DDL outside of migration files is permitted.
- MySQL credentials MUST be stored in environment variables only.
- No hotel availability data, pricing, or room inventories are to be stored in MySQL —
  these are owned by the upstream vendor system.
- Future booking/payment entities (traveller forms, booking records, PG references) MUST
  follow the same Flyway-first migration discipline when introduced.

### VII. Error Handling Must Be Deterministic and Capability-Aware

Every API call to the Spring Boot layer can fail in documented ways. The error handling
strategy MUST cover all documented failure modes without silent swallowing.

**Error taxonomy** (derived from `api/Hotel-Search-doc.md`):

| Code | Condition | Required action |
|---|---|---|
| 400 | Validation error (`WRAPPER_VALIDATION_ERROR`) | Log + surface structured message to user |
| 401 / token expiry | Expired bearer token | Trigger token refresh → retry once |
| 404 | No result (`WRAPPER_NO_RESULT`) | Surface "no results" state to frontend |
| 500 | Internal server / downstream null | Log + surface degraded-state message |
| 502 | Downstream null (`WRAPPER_DOWNSTREAM`) | Log + surface downstream-failure message |
| 504 | Downstream timeout (`WRAPPER_DOWNSTREAM_TIMEOUT`) | Log + surface timeout message |

**Rules**:
- The AI layer MUST map every Spring Boot error shape to a typed internal error model before
  forwarding to the frontend. Raw Spring Boot error payloads MUST NOT be forwarded verbatim.
- SSE streams MUST emit a structured error event (not close silently) on failure so the
  frontend can render an appropriate state.
- Polling interruptions (timeout, downstream failure during poll loop) MUST emit a terminal
  polling-error event and cancel the poll loop cleanly.
- `errorTime` and `apiPath` fields from upstream responses MUST be logged for diagnostics
  but MUST NOT be exposed in frontend-facing error messages.
- Frontend MUST handle all four user-facing states for every async operation: loading,
  partial-success (progressive), empty, and error.

### VIII. Frontend Is a Consumer Layer — Never a Business Logic Layer

The Nuxt 3 / Vue 3 / Tailwind / TypeScript frontend MUST remain a pure presentation and
UX layer.

**Rules**:
- All API calls to the Spring Boot layer MUST be proxied through the FastAPI AI layer via
  SSE or REST — the frontend MUST NOT call the Spring Boot APIs directly.
- Composables MUST encapsulate all API interaction and polling state; raw `fetch`/`axios`
  calls MUST NOT appear in Vue component files (`*.vue`).
- TypeScript strict mode MUST be enabled. `any` type usage MUST be justified with a comment
  and MUST NOT appear in DTO interface files.
- Progressive rendering during polling MUST be implemented via reactive Vue state updates —
  never via full-page re-fetches or page reloads.
- Component files MUST follow the Nuxt 3 composables → components → pages hierarchy; business
  state MUST NOT live in page-level components.
- Tailwind utility classes MUST be the sole styling mechanism; no external CSS frameworks,
  no inline `style` attributes for anything beyond dynamic values.

### IX. Simplicity and YAGNI Govern All Architecture Decisions

This project targets local macOS / Windows development and must remain buildable and runnable
by a single developer without cloud infrastructure.

**Rules**:
- Every new abstraction, service, or module MUST have a concrete, immediate use case — no
  speculative generality.
- The local development stack MUST be launchable with a single command per layer (e.g.
  `docker compose up`, `npm run dev`, `uvicorn ...`). Complex multi-step bootstrap sequences
  are a constitution violation.
- Redis and MySQL MUST be run via Docker for local development. No expectation of pre-installed
  system services.
- Feature flags, plugin architectures, and event buses are not permitted in MVP scope unless
  they directly enable a documented future-scope item from `api/hotel-search-flow.md`.
- When two implementation approaches both satisfy requirements, the simpler one MUST be chosen.
  Complexity MUST be justified in the plan's Complexity Tracking table.

### X. Architecture Must Be Extensible for Documented Future Scope

The MVP MUST NOT close off the following documented future-scope items from
`api/hotel-search-flow.md` and `architecture/ai-orchestration.md`:

| Future capability | Architectural pre-condition |
|---|---|
| Fare recheck | Search session state (searchKey, cacheKey) MUST be retrievable post-poll |
| Traveller forms | Persistence layer MUST support traveller entity addition via Flyway migration |
| Booking APIs | AI orchestration graph MUST support new LangGraph node insertion without refactor |
| Payment / PG orchestration | AI layer MUST NOT embed payment logic; PG redirection URL handling is sufficient for MVP |
| Vouchers | No pre-work required; future Flyway migration path must remain open |
| AI personalisation / RAG | Redis memory schema MUST use keyed namespaces to allow future embedding storage |
| Multilingual / Voice AI | Conversational state MUST be language-agnostic in data model |

**Rule**: Any MVP implementation decision that structurally prevents one of the above
extensions MUST be escalated and documented before merging. "We can refactor later" is not
an acceptable justification for blocking an extension point.

## Technical Stack & Canonical API Reference

### Approved Technology Stack

| Layer | Technology | Version / Constraint |
|---|---|---|
| Frontend framework | Nuxt 3 | Latest stable |
| UI framework | Vue 3 (Composition API) | Bundled with Nuxt 3 |
| Styling | Tailwind CSS | Latest stable; no other CSS frameworks |
| Frontend language | TypeScript | Strict mode required |
| AI orchestration | FastAPI | Latest stable |
| AI graph | LangGraph | Latest stable |
| LLM SDK | OpenAI SDK (Python) | Latest stable |
| Streaming | Server-Sent Events (SSE) | Via FastAPI `EventSourceResponse` |
| Session memory | Redis | 7.x; Docker for local dev |
| Relational DB | MySQL | 8.x; Docker for local dev |
| DB migrations | Flyway | Managed migrations only |
| Backend (existing) | Spring Boot | Source of truth — read-only from this project |

No technology outside this table may be introduced without a constitution amendment.

### Canonical Source Documents (Read-Only)

The following documents are locked as architectural source of truth. They MUST NOT be
modified by feature branches — only by explicit backend or architecture decisions recorded
separately:

- `api/Hotel-Search-doc.md` — Full API contract reference (DTOs, error shapes, endpoints)
- `api/hotel-search-flow.md` — Search lifecycle rules, MVP scope, future scope
- `architecture/ai-orchestration.md` — AI layer responsibilities, technology stack,
  polling flow, error handling, future scope

### MVP Scope Boundary

**In scope** (from `api/hotel-search-flow.md`):
- Conversational hotel search
- Hotel listing (progressive, polling-backed)
- Hotel details
- Room details
- Search history logging
- External PG redirection

**Explicitly out of scope for MVP**:
- Booking confirmation
- Fare recheck
- Payment execution
- Vouchers
- Cancellation flows

Any implementation that starts work on out-of-scope items without a constitution amendment
and separate feature branch is a violation.

## Local Development Standards

### Environment Setup Requirements

- All infrastructure (Redis, MySQL) MUST run via Docker Compose. A `docker-compose.yml` at
  the repository root MUST define all required services.
- A `.env.example` file MUST exist at the repository root documenting every required
  environment variable. A `.env` MUST NOT be committed to source control.
- Required environment variables MUST include at minimum:
  - `HOTEL_API_BASE_URL` — Spring Boot wrapper base URL
  - `HOTEL_API_MODULE_ID`, `HOTEL_API_USERNAME`, `HOTEL_API_PASSWORD` — Token credentials
  - `REDIS_URL` — Redis connection string
  - `MYSQL_HOST`, `MYSQL_PORT`, `MYSQL_DB`, `MYSQL_USER`, `MYSQL_PASSWORD`
  - `OPENAI_API_KEY`

### Project Directory Layout

```
ai-chat/
├── frontend/               # Nuxt 3 application
│   ├── composables/        # All API + polling logic
│   ├── components/         # Reusable UI components
│   ├── pages/              # Route-level pages only
│   └── types/              # TypeScript DTO interfaces
├── ai-service/             # FastAPI + LangGraph orchestration
│   ├── agents/             # LangGraph graph definitions
│   ├── services/           # Per-capability API call modules
│   ├── models/             # Pydantic DTO models
│   └── memory/             # Redis session management
├── db/
│   └── migrations/         # Flyway versioned SQL migrations
├── docker-compose.yml
└── .env.example
```

### Running Locally

- **Infrastructure**: `docker compose up -d`
- **AI service**: `uvicorn ai-service.main:app --reload --port 8000`
- **Frontend**: `npm run dev` (from `frontend/`)
- Each layer MUST start independently with a single command. Dependency on a running
  layer from another layer MUST be handled with graceful startup retries, not hard failures.

### Cross-Platform Compatibility

- All shell scripts MUST use POSIX-compatible syntax (no bash-only features unless noted).
- File paths in code MUST use `/` separators or path utilities — no hard-coded backslashes.
- Docker Compose MUST handle volume mounts in a way that works on both macOS and Windows
  (avoid host-path assumptions).

## Governance

This constitution supersedes all other informal practices, README guidance, or verbal
decisions for the NexTrip AI project. When a practice conflicts with this constitution,
the constitution wins — or an amendment is raised.

### Amendment Procedure

1. Open a dedicated branch named `constitution/vX.Y.Z-<short-description>`.
2. Edit `.specify/memory/constitution.md` directly; update the version, ratification date,
   and last-amended date.
3. Update all dependent templates (`plan-template.md`, `spec-template.md`,
   `tasks-template.md`) in the same branch if the amendment affects their gates or
   categories.
4. Record the rationale for the amendment in the commit message and pull request description.
5. The amendment MUST be reviewed and approved before merging; self-merges are not permitted
   for MAJOR version bumps.

### Versioning Policy

- **MAJOR**: Removal or redefinition of a principle; breaking change to an approved
  technology; removal of an API from the canonical stack.
- **MINOR**: Addition of a new principle or technology; material expansion of governance
  guidance; addition of a new canonical source document.
- **PATCH**: Clarifications, wording improvements, formatting fixes, adding examples without
  semantic change.

### Compliance Review Expectations

- Every pull request MUST include a "Constitution Check" section (using the gate from
  `plan-template.md`) confirming no principles are violated.
- If a violation is necessary and justified, it MUST be documented in the plan's Complexity
  Tracking table and an amendment MUST be filed concurrently.
- `speckit.analyze` SHOULD be run before any significant merge to surface cross-artifact
  consistency issues.

---

**Version**: 1.0.0 | **Ratified**: 2026-05-23 | **Last Amended**: 2026-05-23

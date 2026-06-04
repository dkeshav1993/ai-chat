# Implementation Plan: AI-Powered Hotel Discovery Platform (NexTrip AI)

**Branch**: `001-ai-hotel-discovery-platform` | **Date**: 2026-05-23 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `specs/001-ai-hotel-discovery-platform/spec.md`

## Summary

Build NexTrip AI — a conversational, AI-orchestrated hotel discovery platform. A user types a natural-language hotel search in a Nuxt 3 chat UI. A FastAPI + LangGraph AI service interprets the intent, calls the existing Spring Boot wrapper APIs in the correct sequence (AutoSuggest → Search → Background Status poll loop → Search By Poll), and streams incremental hotel results to the frontend via SSE. Hotel and room details are fetched on demand. All search events are logged asynchronously to MySQL. Token lifecycle, polling lifecycle, and error handling are fully managed by the AI service layer — the frontend is a pure consumer.

The MVP is launchable locally with three commands (Docker Compose + uvicorn + npm run dev) on macOS or Windows. No cloud infra, no Kubernetes, no distributed complexity.

---

## Technical Context

**Language/Version**: TypeScript strict (Nuxt 3 / Vue 3 frontend) + Python 3.11 (FastAPI AI service)

**Primary Dependencies**: Nuxt 3 (latest stable), Vue 3 Composition API, Tailwind CSS, FastAPI, LangGraph (latest stable), OpenAI SDK (Python), `httpx` (async HTTP client for Spring Boot calls), `sse-starlette` (SSE streaming), Redis 7 (session/token/polling state), MySQL 8 (search history), Flyway (migrations), Docker Compose

**Storage**:
- **Redis 7**: Bearer token cache (with TTL), per-session conversational memory (chat turns), per-session polling state (searchKey / cacheKey / autoSuggestId / poll iteration / status). Keys are namespaced: `traversia:token`, `traversia:session:{sessionId}:memory`, `traversia:session:{sessionId}:poll`.
- **MySQL 8**: `search_history` table (destination, dates, rooms, session ID, timestamp). Writes are async fire-and-forget; never on the critical path. Schema managed exclusively through Flyway versioned migrations.

**Testing**: Vitest (frontend unit/composable tests), pytest (AI service unit + integration tests)

**Target Platform**: macOS / Windows (Docker Compose for Redis + MySQL). No cloud services required locally.

**Performance Goals**:
- First hotel card renders within 5 s of search query submission
- SSE event latency < 500 ms per emitted event
- Progressive rendering begins before poll loop completes
- Token auto-refresh adds < 200 ms overhead on a single retry

**Constraints**:
- AI layer MUST NOT modify Spring Boot DTO fields in any direction
- Polling timeout: configurable, default 60 s
- Frontend MUST NOT call Spring Boot APIs directly under any circumstance
- Redis and MySQL MUST run via Docker; no expectation of locally installed services

**Scale/Scope**: Single-tenant MVP. One concurrent active search session per user. Redis namespacing designed to support future multi-session isolation without refactor.

---

## Constitution Check

*GATE: Pre-design verification — all gates ✅ confirmed against spec, source API docs, and architecture documents.*

| # | Gate | Status |
|---|---|---|
| I | No new API endpoints invented — all calls target the canonical Spring Boot wrapper | ✅ |
| I | Request/response DTO shapes match `api/Hotel-Search-doc.md` exactly | ✅ |
| II | AI layer contains no business logic, pricing, payment, or direct DB access | ✅ |
| III | Polling flow preserved: AutoSuggest → Search → BackgroundStatus loop → SearchByPoll | ✅ |
| III | `searchKey`, `cacheKey`, `autoSuggestId` carried through entire poll lifecycle | ✅ |
| IV | Token refresh handled by shared module; retry-once on expiry; credentials in env vars | ✅ |
| V | Pydantic models and TypeScript interfaces mirror DTO contracts; updated in same commit | ✅ |
| VI | MySQL writes are async and limited to search history / session metadata | ✅ |
| VI | All schema changes go through Flyway versioned migrations | ✅ |
| VII | All documented error codes (400/401/404/500/502/504) handled with typed error model | ✅ |
| VII | SSE stream emits structured error event on failure (no silent close) | ✅ |
| VIII | Frontend calls Spring Boot only through FastAPI AI layer — never directly | ✅ |
| VIII | All API/polling logic in composables — not in `.vue` component files | ✅ |
| IX | Feature is launchable with single command per layer; no cloud infra required locally | ✅ |
| X | No implementation decision structurally blocks a documented future-scope capability | ✅ |

---

## Project Structure

### Documentation (this feature)

```text
specs/001-ai-hotel-discovery-platform/
├── plan.md              ← this file
├── research.md          ← Phase 0 output
├── data-model.md        ← Phase 1 output
├── quickstart.md        ← Phase 1 output
├── contracts/           ← Phase 1 output
│   ├── sse-events.md
│   └── fastapi-endpoints.md
└── tasks.md             ← Phase 2 output (/speckit.tasks — not created here)
```

### Repository Root Structure

```text
ai-chat/
├── frontend/                          # Nuxt 3 application
│   ├── composables/
│   │   ├── useHotelSearch.ts          # Search intent → SSE stream subscription
│   │   ├── usePollingState.ts         # Poll status, hotel card accumulation
│   │   ├── useHotelDetails.ts         # Hotel detail fetch + error states
│   │   ├── useRoomDetails.ts          # Room detail fetch + error states
│   │   └── useChat.ts                 # Conversational turn management
│   ├── components/
│   │   ├── chat/
│   │   │   ├── ChatInput.vue
│   │   │   ├── ChatBubble.vue
│   │   │   └── ChatWindow.vue
│   │   ├── hotels/
│   │   │   ├── HotelCard.vue
│   │   │   ├── HotelList.vue
│   │   │   ├── HotelDetail.vue
│   │   │   └── HotelCardSkeleton.vue
│   │   ├── rooms/
│   │   │   ├── RoomCard.vue
│   │   │   └── RoomList.vue
│   │   └── shared/
│   │       ├── LoadingState.vue
│   │       ├── ErrorState.vue
│   │       └── EmptyState.vue
│   ├── pages/
│   │   ├── index.vue                  # Chat + search entry point
│   │   ├── hotels/
│   │   │   └── [hotelId].vue          # Hotel detail page
│   │   └── hotels/
│   │       └── [hotelId]/rooms.vue    # Room detail page
│   ├── types/
│   │   ├── hotel.ts                   # TypeScript DTO interfaces (mirrors Pydantic models)
│   │   ├── search.ts
│   │   ├── room.ts
│   │   └── sse.ts                     # SSE event type definitions
│   ├── utils/
│   │   └── correlationId.ts           # UUID v4 generator for correlationId
│   ├── nuxt.config.ts
│   ├── tailwind.config.ts
│   └── tsconfig.json
│
├── ai-service/                        # FastAPI + LangGraph AI orchestration
│   ├── main.py                        # FastAPI app entry point
│   ├── routers/
│   │   ├── chat.py                    # POST /chat/search — SSE stream endpoint
│   │   ├── hotels.py                  # GET /hotels/{hotelId} — hotel details
│   │   └── rooms.py                   # GET /hotels/{hotelId}/rooms — room details
│   ├── agents/
│   │   └── hotel_search_graph.py      # LangGraph StateGraph: intent → search → poll → stream
│   ├── services/
│   │   ├── token_service.py           # Shared bearer token manager (Redis-backed, retry-once)
│   │   ├── autosuggest_service.py     # Calls /fetchAutoSuggest
│   │   ├── search_service.py          # Calls /hotels/search
│   │   ├── poll_service.py            # Calls /backgroundProcessStatus + /search-by-poll
│   │   ├── hotel_detail_service.py    # Calls /getHotelDetails
│   │   ├── room_detail_service.py     # Calls /getRoomDetails
│   │   └── history_service.py         # Async MySQL write for search_history
│   ├── models/
│   │   ├── hotel.py                   # Pydantic models mirroring Spring Boot DTOs
│   │   ├── search.py
│   │   ├── room.py
│   │   └── errors.py                  # Typed internal error model
│   ├── memory/
│   │   ├── redis_client.py            # Redis connection + key helpers
│   │   ├── session_memory.py          # Conversational turn read/write
│   │   └── poll_state.py              # searchKey/cacheKey/autoSuggestId CRUD
│   ├── db/
│   │   └── mysql_client.py            # Async MySQL pool (aiomysql)
│   ├── config.py                      # Env var loading (pydantic-settings)
│   └── requirements.txt
│
├── db/
│   └── migrations/                    # Flyway versioned SQL migrations
│       └── V1__create_search_history.sql
│
├── docker-compose.yml                 # Redis + MySQL services
├── .env.example                       # All required env vars documented
└── .env                               # Local values — gitignored
```

**Structure Decision**: Three-layer web application. Frontend (Nuxt 3) consumes the AI service (FastAPI) via SSE and REST. AI service consumes the existing Spring Boot wrapper via async httpx. Persistence (Redis + MySQL) is service-layer only — never accessed from frontend. Each layer starts with one command.

---

## Key Lifecycle Definitions

### Token Lifecycle

```
Startup
  └─ token_service.py: call Token API → store token in Redis key "traversia:token" with TTL
                                                                    ↓
Every outbound httpx call
  └─ token_service.get_token() → read from Redis (cache hit)
                               → on miss: call Token API → refresh Redis → return token
                                                                    ↓
On 401 / "token expired" in any API response
  └─ token_service.refresh_and_retry(request_fn)
       1. Call Token API → overwrite Redis key
       2. Retry original request exactly once with new token
       3. If retry fails → raise typed TokenRefreshError → propagated to SSE stream as error event
```

Token credentials (`moduleID`, `userName`, `password`) loaded exclusively from env vars via `config.py`. Never appear in source code.

---

### correlationId Lifecycle

```
Frontend (TypeScript):
  └─ utils/correlationId.ts: uuidv4() on every outbound fetch to FastAPI

FastAPI router:
  └─ Receives correlationId from frontend request
  └─ Passes correlationId through to every Spring Boot API call
  └─ Logs correlationId alongside every request + response (structlog)
  └─ Returns correlationId in every SSE event payload for traceability

Spring Boot responses:
  └─ "correlationId" field echoed back → logged by AI service
  └─ Never re-shaped or aliased — consumed as-is per constitution Principle V
```

---

### searchKey / cacheKey / autoSuggestId Lifecycle

```
Step 1 — AutoSuggest
  Input:  { correlationId, payload: { autoSuggestKey: <destination string> } }
  Output: autoSuggestId, autoSuggests[{ uniqueId, type, name, cityName, ... }]
  Store:  Redis "traversia:session:{sessionId}:poll" → { autoSuggestId, autosuggestIdentifier }

Step 2 — Search
  Input:  { correlationId, payload: { autoSuggestId, checkIn, checkOut,
            autosuggestIdentifier: { uniqueIdentifier, type, name }, rooms } }
  Output: searchKey, cacheKey (inside payload.data)
  Store:  Redis "traversia:session:{sessionId}:poll" → add { searchKey, cacheKey, pollIteration: 0 }

Step 3 — Background Process Status (loop)
  Input:  { correlationId, payload: { cacheKey, searchKey, autoSuggestId } }
  Poll:   Every 2 s. Terminate when payload.data.inProgress === false OR elapsed > 60 s
  Update: Redis pollIteration counter on each successful check

Step 4 — Search By Poll
  Input:  same { searchKey, cacheKey, autoSuggestId }
  Output: incremental hotel batches → emitted as SSE events to frontend
  Cleanup: On poll loop termination (normal or timeout), Redis poll key is NOT deleted
           (preserves searchKey/cacheKey for future fare-recheck extension — Principle X)
```

---

### Polling Lifecycle (AI Service)

```
hotel_search_graph.py (LangGraph StateGraph)
│
├── Node: extract_intent        ← OpenAI SDK: parse NL query → { destination, checkIn, checkOut, rooms }
├── Node: autosuggest           ← autosuggest_service.py → returns autoSuggestId + identifier
├── Node: trigger_search        ← search_service.py → returns searchKey + cacheKey
├── Node: poll_background_status (loop)
│       ├── call poll_service.check_background_status()
│       ├── if inProgress: sleep 2s → repeat
│       ├── if not inProgress: proceed to fetch_poll_results
│       └── if timeout (60s): emit SSE error event → terminate graph
├── Node: fetch_poll_results    ← poll_service.search_by_poll() → hotel batch
│       └── emit SSE "hotels_batch" event → frontend renders progressively
├── Node: write_search_history  ← history_service.py (asyncio.create_task — fire and forget)
└── Node: stream_complete       ← emit SSE "search_complete" event
```

On any node error: emit structured SSE `"error"` event with typed error code, then terminate gracefully. Stream never closes silently.

---

### SSE Architecture

```
Frontend composable: useHotelSearch.ts
  └─ EventSource("/api/chat/search?sessionId=...&query=...")
       receives events:
         { event: "thinking",        data: { message: "Finding hotels in Mumbai..." } }
         { event: "hotels_batch",    data: { hotels: [...], batchIndex: N } }
         { event: "search_complete", data: { totalHotels: N, searchKey: "...", autoSuggestId: "..." } }
         { event: "error",           data: { code: "POLL_TIMEOUT" | "DOWNSTREAM_NULL" | ...,
                                              message: "...", recoverable: bool } }

FastAPI router: routers/chat.py
  └─ GET /chat/search  (SSE, EventSourceResponse from sse-starlette)
       ├─ validate sessionId
       ├─ launch hotel_search_graph.astream(query, sessionId)
       └─ yield SSE events as graph nodes emit them

Note: GET is used for SSE (EventSource browser API requires GET).
      The search query is passed as a query parameter; session state lives in Redis.
```

---

## Phased Roadmap

### Phase 1 — Infrastructure & Skeleton (local runnable baseline)

Deliverables:
- `docker-compose.yml` with Redis 7 + MySQL 8
- `.env.example` with all required variables
- FastAPI app skeleton: `main.py`, `config.py`, `routers/chat.py` (stub SSE endpoint)
- Nuxt 3 project scaffold with Tailwind, TypeScript strict mode, composable structure
- Flyway `V1__create_search_history.sql` migration
- `token_service.py` — complete token lifecycle (eager fetch, Redis cache, retry-once)
- `redis_client.py` — connection + key helpers
- All three layers startable with one command each

### Phase 2 — AI Search Core (end-to-end search flow)

Deliverables:
- `hotel_search_graph.py` — complete LangGraph StateGraph (all nodes)
- `autosuggest_service.py`, `search_service.py`, `poll_service.py` — full implementations
- `models/hotel.py`, `models/search.py` — Pydantic DTOs matching Spring Boot contracts
- `memory/poll_state.py` — searchKey/cacheKey/autoSuggestId CRUD in Redis
- `history_service.py` — async fire-and-forget MySQL write
- SSE stream: `thinking`, `hotels_batch`, `search_complete`, `error` events
- `useHotelSearch.ts` composable — EventSource subscription + progressive hotel card accumulation
- `HotelCard.vue`, `HotelList.vue`, `HotelCardSkeleton.vue` components
- `pages/index.vue` — chat input + progressive hotel list
- Frontend TypeScript DTO interfaces (mirrors Pydantic models exactly)

### Phase 3 — Hotel & Room Details

Deliverables:
- `hotel_detail_service.py`, `room_detail_service.py` — full implementations
- `models/room.py` — Pydantic DTOs for room details
- `routers/hotels.py`, `routers/rooms.py` — FastAPI REST endpoints
- `useHotelDetails.ts`, `useRoomDetails.ts` composables
- `HotelDetail.vue`, `RoomList.vue`, `RoomCard.vue` components
- `pages/hotels/[hotelId].vue`, `pages/hotels/[hotelId]/rooms.vue`
- PG redirect URL generation + new-tab navigation on room selection
- All four async UI states (loading / partial / empty / error) for every page

### Phase 4 — Hardening & Polish

Deliverables:
- Full error handling coverage: all 400/401/404/500/502/504 codes mapped to `models/errors.py`
- Session memory (`session_memory.py`) — conversational turn persistence in Redis
- Chat disambiguation flow (multiple AutoSuggest results → AI follow-up question)
- 60 s poll timeout with partial-results preservation
- Concurrent search cancellation (new query while poll is active → clean teardown)
- Vitest composable tests, pytest service unit tests
- `correlationId` logging in structured format (structlog) across all AI service calls

---

## DTO Contract Reference

All request/response shapes are frozen from `api/Hotel-Search-doc.md`. Pydantic models and TypeScript interfaces MUST match these exactly.

| Capability | Endpoint | Key Request Fields | Key Response Fields |
|---|---|---|---|
| Token | POST `.../generateToken` | `moduleID`, `userName`, `password` | `token`, `correleationId`, `tokenValid` |
| AutoSuggest | POST `.../fetchAutoSuggest` | `correlationId`, `payload.autoSuggestKey` | `autoSuggestId`, `autoSuggests[].uniqueId/type/name` |
| Hotel Search | POST `.../hotels/search` | `correlationId`, `payload.autoSuggestId/checkIn/checkOut/autosuggestIdentifier/rooms` | `searchKey`, `cacheKey` (in `payload.data`) |
| Background Status | POST `.../backgroundProcessStatus` | `correlationId`, `payload.cacheKey/searchKey/autoSuggestId` | `payload.data.inProgress`, `payload.data.cacheKey` |
| Hotel Details | POST `.../room/getHotelDetails` | `payload.searchKey`, `payload.hotelId` | `payload.hotelData` |
| Room Details | POST `.../room/getRoomDetails` | `payload.autoSuggestId/searchKey/hotelId/filterBySupplier` | `payload.roomData.standardRooms` |

**Note**: `correleationId` (sic — with double-e) is the exact spelling in the Token API response. Pydantic field alias must match this exactly.

---

## Environment Variables Reference

All values stored in `.env`, documented in `.env.example`. Never committed to source control.

```env
# Spring Boot wrapper
HOTEL_API_BASE_URL=https://travelonedev-services.thomascook.in
HOTEL_API_MODULE_ID=Traversia
HOTEL_API_USERNAME=traversia
HOTEL_API_PASSWORD=Traversia@123

# Redis
REDIS_URL=redis://localhost:6379

# MySQL
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_DB=traversia
MYSQL_USER=traversia
MYSQL_PASSWORD=traversia_local

# OpenAI
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o

# App
POLL_TIMEOUT_SECONDS=60
POLL_INTERVAL_SECONDS=2
```

---

## Complexity Tracking

> No constitution violations. No complexity justification required.

---

## Post-Design Constitution Re-check

All 15 gates remain ✅ after Phase 1 design. No amendments required. No out-of-scope items introduced. Future-scope extension points confirmed open:

- LangGraph graph accepts new nodes without refactor (booking, fare-recheck)
- Redis poll state keyed by sessionId (survives for fare-recheck after poll)
- MySQL schema open for Flyway traveller/booking entity migrations
- `filterBySupplier` sent as `[]` — no supplier-specific logic locked in
- `OPENAI_MODEL` is an env var — model swap requires no code change

---
description: "Task list for AI-Powered Hotel Discovery Platform (Traversia)"
---

# Tasks: AI-Powered Hotel Discovery Platform (Traversia)

**Input**: Design documents from `specs/001-ai-hotel-discovery-platform/`

**Prerequisites**: plan.md ✅ | spec.md ✅ | research.md ✅ | data-model.md ✅ | contracts/ ✅

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] [CATEGORY] Description`

- **[P]**: Can run in parallel (different files, no dependencies on incomplete siblings)
- **[Story]**: User story this task belongs to (US1–US4)
- **[CATEGORY]**: `[INFRA]` `[TOKEN]` `[AI-AGENT]` `[API-CALL]` `[POLL]` `[SSE]` `[FRONTEND]` `[DB]` `[ERROR]`

## Path Conventions

- **Frontend**: `frontend/composables/`, `frontend/components/`, `frontend/pages/`, `frontend/types/`, `frontend/utils/`
- **AI service**: `ai-service/agents/`, `ai-service/services/`, `ai-service/models/`, `ai-service/memory/`, `ai-service/routers/`, `ai-service/db/`
- **Database**: `db/migrations/` (Flyway versioned SQL files only)
- **Infrastructure**: `docker-compose.yml`, `.env.example`, `.gitignore`

---

## Phase 1: Setup & Infrastructure

**Purpose**: Create the full project skeleton, Docker infrastructure, and all configuration so every subsequent task has a runnable baseline to build on.

**⚠️ CRITICAL**: All Phase 2+ tasks depend on this phase being complete.

- [x] T001 [INFRA] Create root `.gitignore` covering `.env`, `__pycache__`, `node_modules`, `.venv`, `*.pyc`, `.DS_Store`
- [x] T002 [INFRA] Create `docker-compose.yml` at repo root with three services: `mysql` (8.0, healthcheck), `redis` (7-alpine, healthcheck), `flyway` (latest, depends_on mysql healthy, mounts `./db/migrations:/flyway/sql`, runs migrate command with env vars)
- [x] T003 [INFRA] Create `.env.example` at repo root documenting all required env vars: `HOTEL_API_BASE_URL`, `HOTEL_API_MODULE_ID`, `HOTEL_API_USERNAME`, `HOTEL_API_PASSWORD`, `REDIS_URL`, `MYSQL_HOST`, `MYSQL_PORT`, `MYSQL_DB`, `MYSQL_USER`, `MYSQL_PASSWORD`, `OPENAI_API_KEY`, `OPENAI_MODEL`, `POLL_TIMEOUT_SECONDS`, `POLL_INTERVAL_SECONDS`
- [x] T004 [INFRA] Create `.env` from `.env.example` (local dev values: MySQL/Redis Docker defaults, OPENAI_API_KEY=your-key-here) — confirm file is gitignored
- [x] T005 [P] [INFRA] Initialize Nuxt 3 project in `frontend/` using `npx nuxi@latest init frontend` with TypeScript, then install Tailwind CSS (`@nuxtjs/tailwindcss`), configure `nuxt.config.ts` with `modules: ['@nuxtjs/tailwindcss']` and `nitro.devProxy: { '/api': 'http://localhost:8000' }`
- [x] T006 [P] [INFRA] Create `frontend/tailwind.config.ts` with `content: ['./components/**/*.vue', './pages/**/*.vue', './layouts/**/*.vue', './composables/**/*.ts']` and a minimal color palette (`primary`, `gray`)
- [x] T007 [P] [INFRA] Configure `frontend/tsconfig.json` with `strict: true` and path aliases: `~/*` → `./*`, `@/*` → `./*`
- [x] T008 [P] [INFRA] Create all frontend directory stubs: `frontend/composables/`, `frontend/components/chat/`, `frontend/components/hotels/`, `frontend/components/rooms/`, `frontend/components/shared/`, `frontend/types/`, `frontend/utils/` — add `.gitkeep` to empty dirs
- [x] T009 [P] [INFRA] Create Python virtual environment for AI service: `cd ai-service && python -m venv .venv`. Create `ai-service/requirements.txt` with pinned dependencies: `fastapi`, `uvicorn[standard]`, `sse-starlette`, `langgraph`, `langchain-openai`, `openai`, `httpx`, `redis[asyncio]`, `aiomysql`, `pydantic-settings`, `structlog`, `python-dotenv`, `uuid`
- [x] T010 [P] [INFRA] Create `ai-service/main.py`: FastAPI app instantiation, CORS middleware (`allow_origins=["http://localhost:3000"]`), health endpoint `GET /health → {"status":"ok"}`, router includes (stubs for chat, hotels, rooms), lifespan handler for startup token fetch
- [x] T011 [P] [INFRA] Create `ai-service/config.py` using `pydantic-settings BaseSettings`: fields for all env vars from `.env.example` with types and defaults. Load from `.env` file. Never hardcode credentials.
- [x] T012 [P] [INFRA] Create all AI service directory stubs: `ai-service/routers/`, `ai-service/agents/`, `ai-service/services/`, `ai-service/models/`, `ai-service/memory/`, `ai-service/db/`
- [x] T013 [INFRA] Create `db/migrations/` directory and placeholder `V1__create_search_history.sql` (empty file with comment `-- Phase 5: filled by DB tasks`) so Flyway has a valid migrations directory to mount
- [x] T014 [INFRA] Verify infrastructure: run `docker compose up -d`, confirm `mysql` and `redis` show `healthy`, confirm `flyway` exits with code 0. Document any fix needed in quickstart.md.

**Checkpoint**: `docker compose up -d` succeeds, `curl http://localhost:8000/health` returns `{"status":"ok"}`, `cd frontend && npm run dev` loads http://localhost:3000 with no errors.

---

## Phase 2: Foundational Layer (Blocking Prerequisites)

**Purpose**: Token management, shared HTTP client, Pydantic DTOs, Redis client, and typed error model. Every user story service depends on these. No user story work begins until this phase is complete.

**⚠️ CRITICAL**: Blocks all Phase 3+ tasks.

- [x] T015 [TOKEN] Create `ai-service/models/token.py`: Pydantic models `TokenRequest` (moduleID, userName, password) and `TokenResponse` (token, correleationId [sic — double-e exact match], message, tokenClaims, tokenValid). Field names must match `api/Hotel-Search-doc.md` exactly.
- [x] T016 [TOKEN] Create `ai-service/services/token_service.py`: singleton `TokenService` class with async `get_token()` (Redis cache hit → return; cache miss → call Token API POST `.../authenticationserver/authenticationService/generateToken` → store in Redis key `traversia:token` with TTL 3600s), async `_fetch_and_cache()`, async `refresh_and_retry(call: Callable)` (force-refresh Redis key → call original function once → propagate error if retry also fails). Inject `httpx.AsyncClient` and `redis.asyncio.Redis` via constructor. Credentials from `config.py` only.
- [x] T017 [TOKEN] Wire `TokenService` into `ai-service/main.py` lifespan handler: on startup, call `token_service.get_token()` to eagerly populate Redis cache. Log success/failure with structlog.
- [x] T018 [P] [INFRA] Create `ai-service/memory/redis_client.py`: async Redis connection factory using `redis.asyncio.from_url(settings.REDIS_URL)`, key helper functions: `token_key()`, `session_memory_key(session_id)`, `session_poll_key(session_id)`. All keys prefixed `traversia:`.
- [x] T019 [P] [ERROR] Create `ai-service/models/errors.py`: `ErrorCode` enum (VALIDATION_ERROR, TOKEN_EXPIRED, NO_RESULT, DOWNSTREAM_NULL, DOWNSTREAM_ERROR, DOWNSTREAM_TIMEOUT, INTERNAL_ERROR, POLL_TIMEOUT, TOKEN_REFRESH_FAILED, NO_AUTOSUGGEST_RESULT), `TraversiaError` Pydantic model (code: ErrorCode, message: str, recoverable: bool, capability: Optional[str]). `message` must be user-safe (never expose apiPath or errorTime from upstream).
- [x] T020 [P] [API-CALL] Create `ai-service/models/search.py`: all Pydantic request/response DTOs for AutoSuggest, HotelSearch, and BackgroundStatus as documented in `api/Hotel-Search-doc.md`. Include: `AutoSuggestEntry`, `AutoSuggestRequest/Response`, `AutosuggestIdentifier`, `RoomGuest`, `Room`, `HotelCard`, `HotelSearchRequest/Response`, `BackgroundStatusRequest/Response`, `BackgroundStatusData`. Field names must be exact character-for-character matches to the Spring Boot contract.
- [x] T021 [P] [API-CALL] Create `ai-service/models/hotel.py`: Pydantic models for `HotelDetailsRequest` (payload: {searchKey, hotelId}), `HotelDetailsResponse` (capability, success, status, message, correlationId, payload.hotelData as `Any`). Field names match `api/Hotel-Search-doc.md` exactly.
- [x] T022 [P] [API-CALL] Create `ai-service/models/room.py`: Pydantic models for `RoomDetailsRequest` (payload: {autoSuggestId, searchKey, hotelId, filterBySupplier: List[str] = []}), `RoomDetailsResponse` (capability, success, status, message, correlationId, payload.roomData.standardRooms as `Any`). Field names match `api/Hotel-Search-doc.md` exactly.
- [x] T023 [P] [FRONTEND] Create `frontend/types/search.ts`: TypeScript interfaces `AutoSuggestEntry`, `HotelCard`, `SearchHistoryEntry` mirroring `ai-service/models/search.py` Pydantic models exactly. Add `export` keyword to all interfaces.
- [x] T024 [P] [FRONTEND] Create `frontend/types/sse.ts`: TypeScript types `SearchState` union ('idle'|'searching'|'streaming'|'complete'|'error'), `SseHotelsBatchEvent`, `SseThinkingEvent`, `SseSearchCompleteEvent`, `SseErrorEvent` (with `SseErrorCode` union type covering all ErrorCode values), as documented in `contracts/sse-events.md`.
- [x] T025 [P] [FRONTEND] Create `frontend/types/hotel.ts`: TypeScript interfaces `HotelData` (index signature `[key: string]: unknown`), `HotelDetailsResponse` mirroring `ai-service/models/hotel.py`.
- [x] T026 [P] [FRONTEND] Create `frontend/types/room.ts`: TypeScript interfaces `RoomOption` (index signature), `RoomData` (hotelId: string, standardRooms: RoomOption[]).
- [x] T027 [P] [FRONTEND] Create `frontend/utils/correlationId.ts`: export function `generateCorrelationId(): string` using `crypto.randomUUID()`. No library dependency.

**Checkpoint**: `ai-service/models/` contains all four Pydantic files with correct field names. `TokenService` starts without error and logs a successful token fetch. `frontend/types/` contains four TypeScript files with no `any` usage in DTO fields. All files pass TypeScript strict mode check (`npx tsc --noEmit` in `frontend/`).

---

## Phase 3: User Story 1 — Conversational Hotel Search (Priority: P1) 🎯 MVP

**Goal**: A user types a natural-language hotel query and sees hotel cards progressively rendering via SSE-backed polling. This is the complete core search flow: AutoSuggest → Search → Poll loop → SSE stream → progressive hotel cards.

**Independent Test**: Type "Find me a hotel in Mumbai from 20 October to 23 October for 2 adults" in the chat UI. Verify hotel cards start appearing within 5 seconds, new cards keep appearing during polling, and a "search complete" state is reached. Verify Redis key `traversia:session:{id}:poll` contains `searchKey`, `cacheKey`, and `autoSuggestId`.

### Implementation for User Story 1

- [x] T028 [P] [US1] [API-CALL] Create `ai-service/services/autosuggest_service.py`: async `call_autosuggest(destination_keyword: str, correlation_id: str, token: str) -> AutoSuggestResponse`. Calls `POST /api/v1/wrapper/landing/fetchAutoSuggest` with exact request envelope `{correlationId, payload: {autoSuggestKey}}`. Handles 400/500 error shapes from `api/Hotel-Search-doc.md`. On `success: false` with "no matching suggestions" message, raises `TraversiaError(code=NO_AUTOSUGGEST_RESULT)`. On 500 downstream null, raises `TraversiaError(code=DOWNSTREAM_NULL)`. Always passes token as Bearer header.
- [x] T029 [P] [US1] [API-CALL] Create `ai-service/services/search_service.py`: async `call_hotel_search(payload: HotelSearchPayload, correlation_id: str, token: str) -> HotelSearchResponse`. Calls `POST /api/v1/wrapper/hotels/search` with exact request envelope. Extracts `searchKey` and `cacheKey` from `response.payload.data`. Handles all documented error shapes (404 no hotels, 500 downstream null, 400 validation). Maps each to appropriate `TraversiaError`.
- [x] T030 [P] [US1] [POLL] Create `ai-service/services/poll_service.py`: two async functions: (1) `check_background_status(cache_key, search_key, auto_suggest_id, correlation_id, token) -> BackgroundStatusResponse` — calls `POST /api/v1/wrapper/hotels/backgroundProcessStatus`, handles all 400/500/504 error shapes; (2) `search_by_poll(search_key, cache_key, auto_suggest_id, correlation_id, token) -> HotelSearchResponse` — calls Search By Poll endpoint with same lifecycle keys. Both functions apply the same token-refresh-and-retry pattern via `token_service`.
- [x] T031 [P] [US1] [INFRA] Create `ai-service/memory/poll_state.py`: async Redis hash CRUD: `save_poll_state(session_id, state_dict)`, `get_poll_state(session_id) -> dict`, `update_poll_iteration(session_id)`, `clear_poll_state(session_id)`. Uses `session_poll_key(session_id)` from `redis_client.py`. TTL 86400s on every write.
- [x] T032 [US1] [AI-AGENT] Create `ai-service/agents/hotel_search_graph.py`: define `SearchState` TypedDict (session_id, correlation_id, query, destination, check_in, check_out, adult_count, child_count, room_count, auto_suggest_id, autosuggest_identifier, autosuggest_candidates, search_key, cache_key, poll_iteration, poll_start_time, poll_in_progress, hotels, is_search_complete, error). Implement all LangGraph `StateGraph` nodes: `extract_intent` (OpenAI SDK call to parse NL query → structured intent), `autosuggest` (calls `autosuggest_service`), `trigger_search` (calls `search_service`), `poll_background_status` (calls `poll_service.check_background_status`, sets `poll_in_progress`, checks timeout via `time.time() - poll_start_time > settings.POLL_TIMEOUT_SECONDS`), `fetch_poll_results` (calls `poll_service.search_by_poll`, appends hotels to state), `write_history` (fires `asyncio.create_task` for history write), `error_handler` (formats `TraversiaError` into state). Wire conditional edges: `poll_background_status` → loop back if `poll_in_progress`, → `fetch_poll_results` if not, → `error_handler` if timeout or error. Compile graph with `graph.compile()`.
- [x] T033 [US1] [SSE] Create `ai-service/routers/chat.py`: `GET /chat/search` endpoint returning `EventSourceResponse`. Accepts query params `session_id: str` and `query: str`. Creates async generator that streams events from `hotel_search_graph.astream()`: yield `thinking` events on intent/autosuggest nodes, yield `hotels_batch` events on each `fetch_poll_results` node output (with `batchIndex`), yield `search_complete` event with `totalHotels`, `searchKey`, `autoSuggestId` on completion, yield structured `error` event (never silent close) on any `TraversiaError`. Register router in `main.py`.
- [x] T034 [US1] [FRONTEND] Create `frontend/composables/useHotelSearch.ts`: exports `{ hotels, searchState, searchError, thinkingMessage, startSearch, cancelSearch }`. `startSearch(query, sessionId)` closes any existing `EventSource`, resets state, opens `new EventSource('/api/chat/search?...')`. Event listeners for `thinking` (update `thinkingMessage`), `hotels_batch` (push to `hotels` array, set state to `streaming`), `search_complete` (set state to `complete`, store `searchKey`/`autoSuggestId` in composable), `error` (set state to `error`, set `searchError`). `onerror` handler for network-level failures. `cancelSearch()` closes EventSource cleanly. All state as Vue `ref`.
- [x] T035 [P] [US1] [FRONTEND] Create `frontend/components/hotels/HotelCard.vue`: accepts `hotel: HotelCard` prop. Renders: hotel name (bold), city, star rating (render as filled/empty circles or numeric), price with currency, available rooms badge. Tailwind only. Emit `select` event on click (passes `hotelId`). No API calls in component.
- [x] T036 [P] [US1] [FRONTEND] Create `frontend/components/hotels/HotelCardSkeleton.vue`: animated Tailwind `animate-pulse` skeleton matching `HotelCard.vue` layout. Shown during `searching` state.
- [x] T037 [P] [US1] [FRONTEND] Create `frontend/components/hotels/HotelList.vue`: accepts `hotels: HotelCard[]` and `searchState: SearchState` props. Renders `HotelCardSkeleton` list (3 items) when state is `searching`, renders `HotelCard` components progressively as hotels arrive (using `v-for` with `:key="hotel.hotelId"`), renders `EmptyState` when state is `complete` and `hotels.length === 0`. Emits `hotel-selected` event with `hotelId`.
- [x] T038 [P] [US1] [FRONTEND] Create `frontend/components/chat/ChatInput.vue`: text input bound to `v-model`, submit button, keyboard shortcut `Enter`. Emits `submit` event with query string. Disabled during `searching` or `streaming` state (pass `disabled: boolean` prop). Tailwind only.
- [x] T039 [P] [US1] [FRONTEND] Create `frontend/components/chat/ChatBubble.vue`: accepts `role: 'user'|'assistant'` and `content: string` props. User bubbles right-aligned, assistant bubbles left-aligned. Tailwind only. No business logic.
- [x] T040 [P] [US1] [FRONTEND] Create `frontend/components/chat/ChatWindow.vue`: accepts `turns: ConversationalTurn[]` prop. Renders `ChatBubble` for each turn. Auto-scrolls to bottom on new turn using `scrollIntoView`. No API calls.
- [x] T041 [P] [US1] [FRONTEND] Create `frontend/components/shared/LoadingState.vue`: generic loading spinner with optional `message: string` prop. Tailwind `animate-spin`. Used across all async states.
- [x] T042 [P] [US1] [FRONTEND] Create `frontend/components/shared/EmptyState.vue`: accepts `title: string` and `message: string` props. Centered layout. Used for no-results states.
- [x] T043 [P] [US1] [FRONTEND] Create `frontend/components/shared/ErrorState.vue`: accepts `error: SseErrorEvent` prop. Shows user-safe `error.message`, shows retry button if `error.recoverable`. Emits `retry` event. Never exposes raw API error details. Tailwind only.
- [x] T044 [US1] [FRONTEND] Create `frontend/composables/useChat.ts`: manages `turns: ConversationalTurn[]` array (ref). `addUserTurn(content)`, `addAssistantTurn(content)`, `addThinkingTurn(message)` functions. `ConversationalTurn` type: `{ role: 'user'|'assistant'|'thinking', content: string, timestamp: number }`.
- [x] T045 [US1] [FRONTEND] Create `frontend/pages/index.vue`: composes `useHotelSearch`, `useChat`. Renders `ChatWindow` (top half), `ChatInput` (bottom), `HotelList` (sidebar or below chat). On `ChatInput` submit: call `addUserTurn`, call `startSearch(query, sessionId)`, show `thinkingMessage` as assistant bubble. On `hotels_batch`: hotels update via reactive `useHotelSearch` composable. On `search_complete`: add summary assistant bubble (e.g., "Found 12 hotels"). On `error`: add error assistant bubble. `sessionId` generated once per page load via `generateCorrelationId()`. No direct API calls in page component.

**Checkpoint**: Full end-to-end search flow works. Hotel cards render progressively. SSE stream emits `thinking`, `hotels_batch`, `search_complete` events. `searchKey`/`cacheKey`/`autoSuggestId` are stored in Redis after search. Frontend shows loading skeleton, then progressive hotel cards, then complete state.

---

## Phase 4: User Story 2 — Hotel Details View (Priority: P2)

**Goal**: User clicks a hotel card and sees the full hotel profile (name, description, amenities, rating, price) fetched from the Hotel Details API.

**Independent Test**: Navigate directly to `/hotels/{knownHotelId}?sessionId={id}`. Verify the hotel profile page loads with `hotelData` content. Test 404 → "details unavailable" state; test 504 → timeout error state.

### Implementation for User Story 2

- [x] T046 [P] [US2] [API-CALL] Create `ai-service/services/hotel_detail_service.py`: async `get_hotel_details(hotel_id: str, search_key: str, correlation_id: str, token: str) -> HotelDetailsResponse`. Calls `POST /api/v1/wrapper/room/getHotelDetails` with exact payload `{payload: {searchKey, hotelId}}`. Handles all documented error shapes: 400 `WRAPPER_VALIDATION_ERROR`, 404 `WRAPPER_NO_RESULT`, 502 `WRAPPER_DOWNSTREAM`, 502 `WRAPPER_DOWNSTREAM_ERROR`, 504 `WRAPPER_DOWNSTREAM_TIMEOUT`, 500 `WRAPPER_INTERNAL_ERROR`. Maps each to `TraversiaError` with appropriate `ErrorCode`. Never forwards raw `apiPath` or `errorTime` to caller.
- [x] T047 [P] [US2] [INFRA] Create `ai-service/memory/session_memory.py`: async functions `get_search_key(session_id) -> str | None` and `get_poll_state(session_id) -> dict | None` — reads from Redis `traversia:session:{id}:poll` hash. Used by hotel/room detail routers to retrieve `searchKey` and `autoSuggestId` without requiring the frontend to pass them as params.
- [x] T048 [US2] [API-CALL] Create `ai-service/routers/hotels.py`: `GET /hotels/{hotelId}` endpoint. Accepts `session_id: str` query param. Retrieves `searchKey` from Redis via `session_memory.get_search_key(session_id)`. Returns 400 if session not found or searchKey missing. Calls `hotel_detail_service.get_hotel_details(...)`. On success: returns `{success: true, capability: "HOTEL_DETAILS", data: {hotelData, searchKey}}`. On `TraversiaError`: returns structured JSON error with `code`, `message`, `recoverable` — HTTP status mapped from error code (404→404, 502→502, 504→504, others→500). Register router in `main.py`.
- [x] T049 [P] [US2] [FRONTEND] Create `frontend/composables/useHotelDetails.ts`: exports `{ hotelData, detailState, detailError, fetchHotelDetails }`. `fetchHotelDetails(hotelId, sessionId)` calls `GET /api/hotels/{hotelId}?sessionId=...`. Manages four states: `idle`, `loading`, `loaded`, `error`. Sets `detailError` on API error response. No direct calls to Spring Boot APIs.
- [x] T050 [P] [US2] [FRONTEND] Create `frontend/components/hotels/HotelDetail.vue`: accepts `hotelData: HotelData` prop. Renders hotel name (h1), all available fields from `hotelData` using `v-for` over object entries (since `hotelData` shape is `Any`/index signature — render key-value pairs in a clean Tailwind grid). "View Rooms" button at bottom emits `view-rooms` event. Tailwind only. No API calls.
- [x] T051 [US2] [FRONTEND] Create `frontend/pages/hotels/[hotelId].vue`: composes `useHotelDetails`. On mount: call `fetchHotelDetails(route.params.hotelId, sessionId)`. Renders `LoadingState` during `loading`, `HotelDetail` on `loaded`, `ErrorState` on `error` (with retry button that re-calls `fetchHotelDetails`), `EmptyState` (title: "Hotel Unavailable", message: "Details not available") for 404. "View Rooms" button navigates to `/hotels/{hotelId}/rooms`. Back link to `/` (search results).

**Checkpoint**: `/hotels/{hotelId}` page loads hotel profile. 404 shows "details unavailable". 504 shows timeout error with retry. Back navigation returns to search results with hotels still visible.

---

## Phase 5: User Story 3 — Room Details & PG Redirect (Priority: P2)

**Goal**: User sees room options for a selected hotel and is redirected to the external payment gateway on room selection.

**Independent Test**: Navigate to `/hotels/{knownHotelId}/rooms?sessionId={id}`. Verify room list renders. Select a room — verify a new browser tab opens to the PG redirect URL. Test 404 → "no rooms available" state.

### Implementation for User Story 3

- [x] T052 [P] [US3] [API-CALL] Create `ai-service/services/room_detail_service.py`: async `get_room_details(hotel_id: str, search_key: str, auto_suggest_id: str, correlation_id: str, token: str) -> RoomDetailsResponse`. Calls `POST /api/v1/wrapper/room/getRoomDetails` with exact payload `{payload: {autoSuggestId, searchKey, hotelId, filterBySupplier: []}}`. Handles all documented error shapes: 400 `WRAPPER_VALIDATION_ERROR` (errors array), 404 `WRAPPER_NO_RESULT`, 502 `WRAPPER_DOWNSTREAM`, 500 `WRAPPER_INTERNAL_ERROR`. Maps to `TraversiaError`. Never exposes raw errorTime/apiPath.
- [x] T053 [US3] [API-CALL] Create `ai-service/routers/rooms.py`: `GET /hotels/{hotelId}/rooms` endpoint. Accepts `session_id: str` query param. Retrieves `searchKey` and `autoSuggestId` from Redis via `session_memory.get_poll_state(session_id)`. Returns 400 if session missing or keys absent. Calls `room_detail_service.get_room_details(...)`. Generates `pgRedirectUrl` (placeholder: `f"https://pg.example.com/redirect?hotelId={hotel_id}&searchKey={search_key}"` — constitution: PG URL generation only, no payment logic). Returns `{success: true, capability: "ROOM_DETAILS", data: {roomData, pgRedirectUrl}}`. On `TraversiaError`: structured error JSON. Register in `main.py`.
- [x] T054 [P] [US3] [FRONTEND] Create `frontend/composables/useRoomDetails.ts`: exports `{ rooms, roomState, roomError, pgRedirectUrl, fetchRoomDetails }`. `fetchRoomDetails(hotelId, sessionId)` calls `GET /api/hotels/{hotelId}/rooms?sessionId=...`. Manages four states: `idle`, `loading`, `loaded`, `error`. Stores `pgRedirectUrl` from response.
- [x] T055 [P] [US3] [FRONTEND] Create `frontend/components/rooms/RoomCard.vue`: accepts `room: RoomOption` prop. Renders room name, key attributes (price, bed type, inclusions) from available fields using `Object.entries(room)`. "Select Room" button emits `select` event passing the room object. Tailwind only.
- [x] T056 [P] [US3] [FRONTEND] Create `frontend/components/rooms/RoomList.vue`: accepts `rooms: RoomOption[]`, `roomState: string`, `pgRedirectUrl: string | null` props. Renders `RoomCard` list with `v-for`. On `RoomCard` `select` event: `window.open(pgRedirectUrl, '_blank')`. Renders `LoadingState`, `EmptyState` (title: "No Rooms Available"), or `ErrorState` based on `roomState`.
- [x] T057 [US3] [FRONTEND] Create `frontend/pages/hotels/[hotelId]/rooms.vue`: composes `useRoomDetails`. On mount: call `fetchRoomDetails(route.params.hotelId, sessionId)`. Renders `LoadingState` during `loading`, `RoomList` on `loaded`, `ErrorState` on `error` with retry, `EmptyState` on 404. Back link to `/hotels/{hotelId}`.

**Checkpoint**: Room list page loads. At least one room card renders. Clicking "Select Room" opens PG redirect URL in new tab. 404 shows "no rooms available" state.

### Mock Provider Integration for Room Details (getRoomDetails API)

The following mock provider enhancements ensure end-to-end `getRoomDetails` works without real Spring Boot APIs:

- [x] MOCK-R01 [MOCK] `ai-service/providers/mock_provider.py` — `room_details()` method: uses regex-based `_destination_key()` and `_regex_match_key()` to resolve any hotel ID format to a destination bucket and a matching mock data entry. Deep-copies data so multiple concurrent requests do not corrupt each other.
- [x] MOCK-R02 [MOCK] `ai-service/mock-data/room-details/{delhi,goa,mumbai,dubai,bangkok}.json` — Each file contains 3 distinct hotel entries (`MOCK-HOTEL-{DEST}-001/002/003`) with realistic room types (STANDARD, SUPERIOR, DELUXE, SUITE), descriptions, pricing, meal plans, occupancy, and refundability. `_meta.regex_patterns` documents which ID patterns map to this file.
- [x] MOCK-R03 [MOCK] `ai-service/routers/rooms.py` — Mock mode tolerance: if Redis session data is absent (e.g. developer navigates directly to rooms URL), placeholder `search_key` and `auto_suggest_id` are synthesised from `hotel_id`. Real mode retains strict Redis session validation.
- [x] MOCK-R04 [MOCK] `ai-service/routers/hotels.py` — Hotel details router now calls `get_provider().hotel_details()` in both mock and real modes (removed hardcoded mock response). Mock provider handles session-less requests with placeholder `search_key`.
- [x] MOCK-R05 [FRONTEND] `frontend/nuxt.config.ts` — `components: [{ path: '~/components', pathPrefix: false }]` added. Fixes Vue component resolution warnings for `<RoomList>`, `<ErrorState>`, `<HotelList>`, `<ChatWindow>` etc. — all components now resolve by filename regardless of subdirectory.

**Regex matching rules for mock hotel IDs:**
- Pattern `MOCK-HOTEL-DELHI-\d+` or `.*delhi.*` → `mock-data/room-details/delhi.json`
- Pattern `MOCK-HOTEL-GOA-\d+` or `.*goa.*` → `mock-data/room-details/goa.json`
- Pattern `MOCK-HOTEL-MUMBAI-\d+` or `.*mumbai.*` or `.*bombay.*` → `mock-data/room-details/mumbai.json`
- Pattern `MOCK-HOTEL-DUBAI-\d+` or `.*dubai.*` → `mock-data/room-details/dubai.json`
- Pattern `MOCK-HOTEL-BANGKOK-\d+` or `.*bangkok.*` → `mock-data/room-details/bangkok.json`
- Any unmatched hotel ID → fallback to `delhi` bucket

---

## Phase 6: User Story 4 — Search History Persistence (Priority: P3)

**Goal**: Every hotel search is silently and asynchronously written to MySQL `search_history` table without blocking the search flow.

**Independent Test**: Perform a hotel search, then run `docker exec -it traversia-mysql mysql -u traversia -ptraversia_local traversia -e "SELECT * FROM search_history ORDER BY created_at DESC LIMIT 5;"`. Verify a record exists with correct destination, dates, session ID, and timestamp.

### Implementation for User Story 4

- [x] T058 [DB] Write `db/migrations/V1__create_search_history.sql`: full CREATE TABLE statement for `search_history` (id BIGINT AUTO_INCREMENT PK, session_id VARCHAR(64) NOT NULL, destination VARCHAR(255) NOT NULL, destination_type VARCHAR(32) NOT NULL, unique_identifier VARCHAR(64) NOT NULL, check_in DATE NOT NULL, check_out DATE NOT NULL, adult_count TINYINT UNSIGNED NOT NULL DEFAULT 1, child_count TINYINT UNSIGNED NOT NULL DEFAULT 0, room_count TINYINT UNSIGNED NOT NULL DEFAULT 1, auto_suggest_id VARCHAR(64) NULL, search_key VARCHAR(64) NULL, created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP, INDEX idx_session_id, INDEX idx_created_at). ENGINE=InnoDB DEFAULT CHARSET=utf8mb4. Run `docker compose restart flyway` to apply.
- [x] T059 [DB] Create `ai-service/db/mysql_client.py`: async `aiomysql` connection pool factory `create_pool(settings: Settings) -> Pool`. Pool size: min=2, max=10. Pool created once on app startup (stored in `app.state.db_pool`). Initialize pool in `main.py` lifespan handler alongside token fetch.
- [x] T060 [US4] [DB] Create `ai-service/services/history_service.py`: `SearchHistoryRecord` dataclass (all fields from V1 migration). Async `write_search_history(record: SearchHistoryRecord, pool: Pool)` function: acquires connection, executes INSERT, commits, closes. Catches all exceptions, logs with structlog (`session_id`, error message), never re-raises. Called via `asyncio.create_task(write_search_history(...))` — fire-and-forget.
- [x] T061 [US4] [AI-AGENT] Update `ai-service/agents/hotel_search_graph.py` node `write_history`: construct `SearchHistoryRecord` from `SearchState` (session_id, destination, destination_type from autosuggest_identifier.type, unique_identifier from autosuggest_identifier.uniqueIdentifier, check_in, check_out, adult_count, child_count, room_count, auto_suggest_id, search_key). Call `asyncio.create_task(history_service.write_search_history(record, app.state.db_pool))`. The task runs in background — graph continues immediately without awaiting completion.

**Checkpoint**: After performing a search, `search_history` table contains a new row. Intentionally disconnecting MySQL and performing a search confirms the search still completes successfully (DB failure does not surface to user).

---

## Phase 7: Error Handling, Resilience & UI States

**Purpose**: Harden all four async states (loading / partial / empty / error) across all screens. Implement 60s poll timeout, concurrent search cancellation, token expiry mid-poll recovery, and complete error code coverage.

- [x] T062 [ERROR] Audit `ai-service/services/autosuggest_service.py`, `search_service.py`, `poll_service.py`: verify all documented error response shapes from `api/Hotel-Search-doc.md` are handled — 400 (WRAPPER_VALIDATION_ERROR), 404 (WRAPPER_NO_RESULT), 500 (internal / downstream null), 502 (WRAPPER_DOWNSTREAM), 504 (WRAPPER_DOWNSTREAM_TIMEOUT). Each must map to the correct `ErrorCode` in `TraversiaError`. No raw Spring Boot error payloads (apiPath, errorTime) forwarded to frontend.
- [x] T063 [POLL] Implement 60s poll timeout in `hotel_search_graph.py` `poll_background_status` node: on each node entry check `time.time() - state['poll_start_time'] > settings.POLL_TIMEOUT_SECONDS`. If exceeded: set `state['error'] = TraversiaError(code=POLL_TIMEOUT, message="Search is taking longer than expected. Showing available results.", recoverable=True)`. Transition to `error_handler` node. Emit `error` SSE event. Partial hotel results already in `state['hotels']` MUST be preserved — continue to `search_complete` with `totalHotels` from partial results before closing stream.
- [x] T064 [TOKEN] Implement mid-poll token expiry recovery: in `poll_service.check_background_status` and `poll_service.search_by_poll`, detect 401 / "token expired" message in response. Call `token_service.refresh_and_retry(lambda: call_original_fn(...))`. If retry succeeds, continue poll loop. If retry fails, raise `TraversiaError(code=TOKEN_REFRESH_FAILED, recoverable=False)`.
- [x] T065 [FRONTEND] Implement concurrent search cancellation in `useHotelSearch.ts`: `startSearch()` must call `cancelSearch()` first (closes existing EventSource), then reset `hotels.value = []`, `searchState.value = 'idle'`, `searchError.value = null`, then open new EventSource. Verify previous hotel cards are cleared before new results appear.
- [x] T066 [AI-AGENT] Implement disambiguation flow in `hotel_search_graph.py` `autosuggest` node: if `AutoSuggestResponse.payload.autoSuggests` has > 1 result with different city names, set `state['autosuggest_candidates'] = autoSuggests` and emit a `thinking` SSE event with message listing disambiguation options (e.g., "Did you mean: Mumbai, Maharashtra or Mumbai, Rajasthan? Please clarify."). For MVP: auto-select the first result and proceed — log the ambiguity for future interactive disambiguation.
- [x] T067 [FRONTEND] Verify all four async UI states are implemented and reachable for each page: `pages/index.vue` (loading skeleton → progressive hotels → complete/empty → error with retry), `pages/hotels/[hotelId].vue` (loading spinner → hotel detail → empty/unavailable → error with retry), `pages/hotels/[hotelId]/rooms.vue` (loading spinner → room list → empty/no rooms → error with retry). Each error state uses `ErrorState.vue` with correct `recoverable` flag from API response.
- [x] T068 [ERROR] Verify SSE stream never closes silently: review `ai-service/routers/chat.py` event generator — ensure every early exit path (any exception, any timeout) yields a structured `error` event before the generator returns. Add `try/except Exception` wrapper around the entire generator body that yields a catch-all `INTERNAL_ERROR` event if an unexpected error escapes.

**Checkpoint**: Timeout after 60s emits `POLL_TIMEOUT` error event with partial results preserved. Token expiry mid-poll is recovered invisibly. New search while old poll is active clears previous results cleanly. All error states are reachable and display correct messages.

---

## Phase 8: Local Validation & Developer Experience

**Purpose**: Ensure the project is runnable by any developer following `quickstart.md` with zero additional steps. Generate README and validate all startup scripts.

- [x] T069 [INFRA] Create `README.md` at repo root: project overview (one paragraph), tech stack table (Frontend/AI Service/Persistence/Backend), quickstart link (`specs/001-ai-hotel-discovery-platform/quickstart.md`), 3-command startup cheatsheet (`docker compose up -d` / `uvicorn...` / `npm run dev`), link to constitution (`specs/001-ai-hotel-discovery-platform/` + `.specify/memory/constitution.md`), link to API source of truth (`api/Hotel-Search-doc.md`).
- [x] T070 [INFRA] Update `specs/001-ai-hotel-discovery-platform/quickstart.md`: fill in exact `uvicorn` command with correct module path (`ai_service.main:app`), confirm Flyway migration output in troubleshooting section, add `docker exec` command to verify `search_history` table exists post-migration.
- [x] T071 [INFRA] Full end-to-end local run validation on macOS: (1) `docker compose up -d` → all healthy; (2) `uvicorn ai_service.main:app --reload --port 8000` → startup logs show token fetched; (3) `cd frontend && npm run dev` → http://localhost:3000 loads; (4) submit a search query → hotel cards appear progressively; (5) click hotel card → hotel detail page loads; (6) click "View Rooms" → room list loads; (7) check `search_history` table → record exists. Document any issues found and fix them.
- [x] T072 [P] [INFRA] Add `.env.example` verification: run `diff <(grep -v '^#' .env.example | grep '=') <(grep -v '^#' .env | grep '=' | sed 's/=.*/=/')` to confirm no undocumented env vars exist in `.env` that are missing from `.env.example`. Fix any gaps.
- [x] T073 [P] [INFRA] Add `frontend/` `package.json` scripts validation: confirm `npm run dev`, `npm run build`, `npm run typecheck` (`nuxi typecheck`) all exist and execute without errors. Fix any TypeScript strict-mode violations found by `typecheck`.

**Checkpoint**: A developer can clone the repo, copy `.env.example` to `.env`, fill in `OPENAI_API_KEY`, run three commands, and complete a full hotel search → details → rooms flow without any additional steps.

---

## Future Scope Tasks (Not MVP — Do Not Implement Until Constitution Amendment)

> These tasks are documented for awareness and architectural pre-conditioning only. They MUST NOT be started without a new feature branch and constitution amendment.

- [ ] FUTURE-01 [API-CALL] Implement `fare_recheck_service.py`: calls fare recheck endpoint (to be added to `api/Hotel-Search-doc.md` when available). Requires `searchKey` + `cacheKey` from Redis poll state — extension point already preserved.
- [ ] FUTURE-02 [DB] Add `V2__create_traveller.sql` Flyway migration: traveller entity (title, firstName, lastName, email, phone, passportNo, sessionId FK). Add `traveller_service.py` for CRUD.
- [ ] FUTURE-03 [API-CALL] Implement `booking_service.py`: calls booking API (to be documented). LangGraph graph supports new node insertion without refactor — `hotel_search_graph.py` wiring is the only change needed.
- [ ] FUTURE-04 [API-CALL] Implement full PG orchestration in `ai-service/routers/rooms.py`: replace placeholder `pgRedirectUrl` with real PG session creation API call. AI layer generates redirect URL only — no payment logic (Principle II).
- [ ] FUTURE-05 [DB] Add `V3__create_booking.sql` Flyway migration: booking entity (bookingRef, sessionId, hotelId, roomType, travellerId, pgTransactionId, status, createdAt).
- [ ] FUTURE-06 [AI-AGENT] Add voucher retrieval node to `hotel_search_graph.py` post-booking: calls voucher API, returns voucher PDF URL via SSE event.
- [ ] FUTURE-07 [AI-AGENT] Implement RAG personalisation: add `traversia:session:{id}:embeddings` Redis key (pre-reserved namespace). Embed search history into vector store for personalised recommendation node in LangGraph graph.
- [ ] FUTURE-08 [FRONTEND] Add multilingual support: extend `useChat.ts` to detect language from user query (via OpenAI). Pass `language` hint through `SearchState`. Conversational state is already language-agnostic in data model.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: No dependencies — start immediately
- **Phase 2 (Foundational)**: Depends on Phase 1 ✅ — **BLOCKS all user story phases**
- **Phase 3 (US1 — Search)**: Depends on Phase 2 ✅ — **BLOCKS Phase 4 and 5** (hotel/room detail need searchKey from search)
- **Phase 4 (US2 — Hotel Details)**: Depends on Phase 2 ✅, benefits from Phase 3 data
- **Phase 5 (US3 — Room Details)**: Depends on Phase 2 ✅, depends on Phase 3 for `autoSuggestId`
- **Phase 6 (US4 — History)**: Depends on Phase 2 ✅ and Phase 3 (uses SearchState from graph)
- **Phase 7 (Error Hardening)**: Depends on Phases 3–6
- **Phase 8 (Validation)**: Depends on all phases

### User Story Dependencies

- **US1 (P1)**: Can start after Phase 2 — no US dependencies
- **US2 (P2)**: Can start after Phase 2 — independently testable; integrates with US1 flow in practice
- **US3 (P2)**: Can start after Phase 2 — requires `autoSuggestId` from US1 poll state
- **US4 (P3)**: Can start after Phase 2 and US1 (needs `hotel_search_graph.py` `write_history` node)

### Within Each Phase

- All `[P]`-marked tasks can run in parallel (different files, no blocking dependencies)
- Models (`models/`) → Services (`services/`) → Routers (`routers/`) → Composables (`composables/`) → Components → Pages
- Pydantic models and TypeScript interfaces MUST be updated in the same commit

### Parallel Opportunities per Phase

**Phase 2** — Can all run in parallel after T014:
```
T015 (token model) + T018 (redis_client) + T019 (errors) + T020 (search models)
+ T021 (hotel models) + T022 (room models) + T023 (TS search types)
+ T024 (TS SSE types) + T025 (TS hotel types) + T026 (TS room types) + T027 (correlationId)
```

**Phase 3** — Parallel within groups:
```
T028 (autosuggest_service) + T029 (search_service) + T030 (poll_service) + T031 (poll_state)
← then T032 (LangGraph graph, depends on T028–T031)
← then T033 (SSE router, depends on T032)
T035 (HotelCard) + T036 (skeleton) + T038 (ChatInput) + T039 (ChatBubble)
+ T040 (ChatWindow) + T041 (LoadingState) + T042 (EmptyState) + T043 (ErrorState)
← then T034 (useHotelSearch) + T044 (useChat)
← then T037 (HotelList, depends on T035) → T045 (index.vue, depends on all above)
```

---

## Parallel Example: Phase 3 (US1)

```bash
# Group A — AI service (run in parallel):
Task T028: "Create ai-service/services/autosuggest_service.py"
Task T029: "Create ai-service/services/search_service.py"
Task T030: "Create ai-service/services/poll_service.py"
Task T031: "Create ai-service/memory/poll_state.py"

# Group B — Frontend shared components (run in parallel with Group A):
Task T035: "Create frontend/components/hotels/HotelCard.vue"
Task T036: "Create frontend/components/hotels/HotelCardSkeleton.vue"
Task T038: "Create frontend/components/chat/ChatInput.vue"
Task T039: "Create frontend/components/chat/ChatBubble.vue"
Task T040: "Create frontend/components/chat/ChatWindow.vue"
Task T041: "Create frontend/components/shared/LoadingState.vue"
Task T042: "Create frontend/components/shared/EmptyState.vue"
Task T043: "Create frontend/components/shared/ErrorState.vue"

# Sequential after Group A:
Task T032: "Create hotel_search_graph.py" → depends on T028–T031
Task T033: "Create routers/chat.py" → depends on T032

# Sequential after Groups A+B:
Task T034: "Create useHotelSearch.ts" → depends on T033
Task T044: "Create useChat.ts"
Task T037: "Create HotelList.vue" → depends on T035
Task T045: "Create pages/index.vue" → depends on T034, T037, T044
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete **Phase 1**: Setup → infrastructure running
2. Complete **Phase 2**: Foundational → token, DTOs, Redis ready
3. Complete **Phase 3**: US1 → full search flow end-to-end
4. **STOP and VALIDATE**: Submit a search query, verify progressive hotel cards, check Redis state
5. Demo: working conversational hotel search

### Incremental Delivery

1. Phase 1 + 2 → Foundation ✅
2. Phase 3 (US1) → Conversational Search MVP ✅ → Demo
3. Phase 4 (US2) → Hotel Details ✅ → Demo
4. Phase 5 (US3) → Room Details + PG Redirect ✅ → Demo
5. Phase 6 (US4) → Search History ✅
6. Phase 7 → Error hardening ✅
7. Phase 8 → Production-ready local build ✅

---

## Notes

- `[P]` = different files, no blocking dependencies on incomplete siblings within same phase
- `[Story]` maps every task to a user story for traceability back to spec.md
- `[CATEGORY]` maps every task to an architectural capability area from the constitution
- Pydantic models and TypeScript interfaces MUST be committed together (Principle V)
- Never call Spring Boot APIs from frontend (Principle VIII) — all calls via `/api/*` proxy to FastAPI
- Token credentials are env vars only — never in source code (Principle IV)
- MySQL writes are fire-and-forget — never block the search/poll critical path (Principle VI)
- SSE stream must always close with an event — never silently (Principle VII)

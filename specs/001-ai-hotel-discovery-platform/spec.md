# Feature Specification: AI-Powered Hotel Discovery Platform

**Feature Branch**: `001-ai-hotel-discovery-platform`

**Created**: 2026-05-23

**Status**: Draft

**Input**: User description: "Enterprise-grade AI-powered hotel discovery platform with conversational search, progressive polling-backed hotel listing, hotel details, room details, search history logging, and external PG redirection — built on Nuxt 3, Vue 3, Tailwind, TypeScript, FastAPI, LangGraph, OpenAI SDK, MySQL, and Flyway."

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 — Conversational Hotel Search (Priority: P1)

A traveller opens the NexTrip AI chat interface and describes a hotel stay in natural language (e.g., "Find me a hotel in Mumbai for 3 nights from 20 October for 2 adults"). The AI layer interprets the intent, resolves the destination via AutoSuggest, triggers a hotel search, and progressively renders matching hotels as results arrive through the polling loop — all without the user having to fill a traditional search form.

**Why this priority**: This is the core differentiating capability of the product. Without conversational search backed by progressive polling, no other user journey is reachable. Every other story depends on a completed search.

**Independent Test**: Can be fully tested by sending a natural-language hotel query in the chat, observing that the AutoSuggest → Search → Poll → progressive hotel cards flow completes end-to-end, and delivering a visible list of hotel cards.

**Acceptance Scenarios**:

1. **Given** a user types a hotel search query in natural language, **When** the AI layer extracts destination, check-in date, check-out date, and room/guest details, **Then** the system calls AutoSuggest with the resolved destination keyword and returns at least one valid `autoSuggestId` with destination identifiers.
2. **Given** a valid `autoSuggestId` and search parameters, **When** the Search API is called, **Then** the system receives `searchKey`, `cacheKey`, and `autoSuggestId` to begin the poll lifecycle.
3. **Given** an active poll lifecycle, **When** the Background Process Status API returns `inProgress: false`, **Then** the polling loop terminates and no further poll requests are made.
4. **Given** an active poll lifecycle, **When** the Search By Poll API returns incremental hotel results, **Then** the frontend renders each batch of hotel cards progressively without waiting for polling to complete.
5. **Given** a polling loop that has been active for 60 seconds, **When** the timeout threshold is reached, **Then** the system emits a terminal polling-error event, cancels the loop cleanly, and the frontend renders a graceful timeout message with partial results already received.
6. **Given** a user query for an unknown destination, **When** AutoSuggest returns no matching suggestions (status 500 with `"autosuggest returned no matching suggestions"`), **Then** the AI replies with a conversational message indicating the destination was not found and prompts the user to try again.

---

### User Story 2 — Hotel Details View (Priority: P2)

After seeing the search results, a traveller clicks on a specific hotel card to view its full profile — images, amenities, location, rating, description, and pricing information — before deciding to explore room options.

**Why this priority**: Hotel details are a necessary intermediate step between search results and room selection. Users cannot make an informed booking decision without this information.

**Independent Test**: Can be tested by passing a known `hotelId` + `searchKey` to the hotel details capability and verifying the full hotel profile renders in the UI.

**Acceptance Scenarios**:

1. **Given** a hotel card is displayed in search results, **When** the user selects it, **Then** the system calls the Hotel Details API (`/api/v1/wrapper/room/getHotelDetails`) with the current `searchKey` and `hotelId`, and the hotel detail page renders with the returned `hotelData`.
2. **Given** the Hotel Details API returns a 404 (`WRAPPER_NO_RESULT`), **When** the hotel page attempts to load, **Then** the frontend renders a "details unavailable" state with a prompt to return to results.
3. **Given** the Hotel Details API returns a 504 (`WRAPPER_DOWNSTREAM_TIMEOUT`), **When** the page loads, **Then** the frontend renders a timeout error state with an option to retry.
4. **Given** the Hotel Details API returns a 502 (`WRAPPER_DOWNSTREAM`), **When** the page loads, **Then** the frontend surfaces a downstream-failure message and does not expose raw `apiPath` or `errorTime` fields to the user.

---

### User Story 3 — Room Details View (Priority: P2)

After viewing a hotel's profile, the traveller explores available room categories and their pricing to compare options before being redirected to the payment gateway.

**Why this priority**: Room selection is the final decision-making step in the MVP flow before external PG redirection. Without it, the user cannot progress to payment.

**Independent Test**: Can be tested by calling the Room Details capability with a valid `hotelId`, `searchKey`, and `autoSuggestId` and verifying that at least one room category renders with name, price, and availability.

**Acceptance Scenarios**:

1. **Given** a user is on the hotel detail page, **When** they navigate to room options, **Then** the system calls the Room Details API (`/api/v1/wrapper/room/getRoomDetails`) with `autoSuggestId`, `searchKey`, `hotelId`, and an empty `filterBySupplier`, and displays the returned `standardRooms` list.
2. **Given** the Room Details API returns a 400 (`WRAPPER_VALIDATION_ERROR` with `"hotelId must not be null"`), **When** a room list is requested, **Then** the frontend shows a structured validation error message and does not crash.
3. **Given** the Room Details API returns a 404 (`WRAPPER_NO_RESULT`), **When** the room list page loads, **Then** the frontend renders a "no rooms available for this hotel" state.
4. **Given** a user selects a specific room, **When** they confirm selection, **Then** the system generates an external PG redirect URL and navigates the user to the payment gateway in a new tab (PG redirection is the terminal MVP action — no booking confirmation is processed in-app).

---

### User Story 4 — Search History Logging (Priority: P3)

Every hotel search the user performs is silently logged to a persistent search history store so that previous searches are available for future personalisation and auditing.

**Why this priority**: This is a background capability — it does not affect the user's immediate experience but is required for auditability and is a foundation for future AI personalisation. It must not block or slow the search flow.

**Independent Test**: Can be tested by performing a search and querying the search history table to confirm a record was written with the correct destination, dates, rooms, and session ID.

**Acceptance Scenarios**:

1. **Given** a user triggers a hotel search, **When** the AI layer processes the search intent, **Then** the search parameters (destination, check-in, check-out, room/guest config, session ID, timestamp) are written asynchronously to the `search_history` table without blocking the search response.
2. **Given** the async write to `search_history` fails (e.g., DB connectivity issue), **When** the failure occurs, **Then** the search flow continues uninterrupted, the error is logged internally, and no error is surfaced to the user.
3. **Given** multiple concurrent users performing searches, **When** history records are written, **Then** each record is correctly associated with its own session ID and no cross-session data leakage occurs.

---

### Edge Cases

- What happens when the AutoSuggest API returns multiple city matches for an ambiguous destination name (e.g., "Paris")? The AI layer MUST present disambiguation options to the user via a conversational follow-up message rather than auto-selecting the first result.
- What happens if the token is expired mid-poll (i.e., during an active Background Process Status poll)? The token refresh module silently regenerates the token and retries the specific failed poll request once; the poll loop resumes without user-visible interruption.
- What happens if the user sends a second search while a poll loop is still active? The active poll loop MUST be cancelled cleanly, its Redis state cleared, and a new search lifecycle started for the new query.
- What happens when the Search API returns `"no hotels matched the supplied request"` (status 404)? The AI responds conversationally with a no-results message and invites the user to modify dates, destination, or guest count.
- What happens when `filterBySupplier` is populated vs. empty on Room Details calls? For MVP, `filterBySupplier` is always sent as an empty array `[]`; filtering is a future-scope item.

---

## Scope Constraints *(NexTrip AI-specific — mandatory)*

### In-Scope for MVP (from constitution)
- Conversational hotel search (natural-language → AutoSuggest → Search → Poll → listing)
- Hotel listing (progressive, polling-backed, via SSE streaming to frontend)
- Hotel details page
- Room details page
- Search history logging (async, non-blocking)
- External PG redirection (URL generation and navigation only)

### Hard Out-of-Scope for MVP
- Booking confirmation
- Fare recheck
- Payment execution
- Voucher management
- Cancellation flows
- Traveller forms
- AI personalisation / recommendations
- Multilingual support
- Voice AI

### Architectural Non-Negotiables
- All Spring Boot wrapper API calls go through the FastAPI AI layer — the frontend MUST NEVER call wrapper APIs directly.
- Poll lifecycle (`searchKey` + `cacheKey` + `autoSuggestId`) MUST be preserved end-to-end through every step.
- DTOs MUST match `api/Hotel-Search-doc.md` exactly — no field mutations or aliasing.
- Token refresh is automatic and invisible to all feature code; the shared token module handles all token lifecycle events.
- MySQL writes (search history) are async and non-blocking — they MUST NOT introduce latency in the search/poll critical path.
- SSE streams MUST emit structured error events on failure — no silent stream closure.
- Frontend MUST NOT poll Spring Boot APIs directly; the AI layer drives all polling and streams updates via SSE.

---

## Requirements *(mandatory)*

### Functional Requirements

**Conversational Search**

- **FR-001**: The system MUST accept natural-language hotel search queries from users and extract destination, check-in date, check-out date, and room/guest configuration as structured search intent.
- **FR-002**: The system MUST call the AutoSuggest API (`/api/v1/wrapper/landing/fetchAutoSuggest`) using the extracted destination keyword and return valid destination identifiers (`autoSuggestId`, `uniqueId`, `type`) to proceed with search.
- **FR-003**: On ambiguous destination input matching multiple AutoSuggest results, the AI layer MUST present disambiguation choices to the user conversationally and wait for selection before proceeding.
- **FR-004**: The system MUST call the Hotel Search API (`/api/v1/wrapper/hotels/search`) with the resolved `autoSuggestId`, `autosuggestIdentifier`, `checkIn`, `checkOut`, and `rooms` payload, and persist the returned `searchKey`, `cacheKey`, and `autoSuggestId` in Redis session state.

**Polling Lifecycle**

- **FR-005**: The AI layer MUST poll the Background Process Status API (`/api/v1/wrapper/hotels/backgroundProcessStatus`) in a loop using `cacheKey`, `searchKey`, and `autoSuggestId` until `payload.data.inProgress` is `false`.
- **FR-006**: The poll loop MUST terminate after a configurable timeout threshold (default: 60 seconds) even if `inProgress` has not become `false`, emitting a terminal error event.
- **FR-007**: The AI layer MUST call the Search By Poll API after each successful Background Status check to retrieve incremental hotel batches and stream them to the frontend via SSE.
- **FR-008**: The frontend MUST render hotel results progressively as each SSE batch arrives, without waiting for the poll loop to complete.

**Hotel & Room Details**

- **FR-009**: The system MUST call the Hotel Details API (`/api/v1/wrapper/room/getHotelDetails`) with `searchKey` and `hotelId` and render the full hotel profile on the hotel detail page.
- **FR-010**: The system MUST call the Room Details API (`/api/v1/wrapper/room/getRoomDetails`) with `autoSuggestId`, `searchKey`, `hotelId`, and `filterBySupplier: []` and display all returned room categories.
- **FR-011**: On user selection of a room, the system MUST generate an external PG redirection URL and open it in a new browser tab. No booking is processed in-app.

**Token Management**

- **FR-012**: The system MUST eagerly fetch a bearer token from the Token API on startup and store it in Redis with an appropriate TTL.
- **FR-013**: On any API response indicating token expiry, the system MUST silently regenerate the token via the Token API and retry the failed request exactly once. If the retry fails, the error MUST be propagated.
- **FR-014**: Token credentials (`moduleID`, `userName`, `password`) MUST be read from environment variables; they MUST NOT appear in source code or committed configuration files.

**Search History**

- **FR-015**: The system MUST asynchronously log every hotel search event to the `search_history` MySQL table with destination, check-in, check-out, room/guest count, session ID, and timestamp, without blocking the search response.
- **FR-016**: A failure in the async search history write MUST be logged internally and MUST NOT surface as an error to the user or interrupt the search flow.

**Error Handling**

- **FR-017**: The AI layer MUST map all documented Spring Boot error shapes (400, 401/token expiry, 404, 500, 502, 504) to typed internal error models before forwarding to the frontend.
- **FR-018**: SSE streams MUST emit a structured error event (not close silently) on any unrecoverable failure during a poll loop or API call.
- **FR-019**: The frontend MUST handle four user-facing states for every async operation: loading, partial-success (progressive results), empty/no-results, and error.

**DTO Contracts**

- **FR-020**: All request DTOs MUST be sent with exactly the fields documented in `api/Hotel-Search-doc.md`. All response DTOs MUST be consumed as documented — no field aliasing, renaming, or reshaping.
- **FR-021**: Every outgoing API call MUST include a UUID v4 `correlationId` generated per-request, and this ID MUST be logged alongside the request and response for traceability.
- **FR-022**: The `capability` field in every API response MUST be used for response routing/handling; it MUST NOT be ignored.

**Frontend Architecture**

- **FR-023**: All API interactions and polling state MUST be encapsulated in Vue composables; raw fetch/axios calls MUST NOT appear in Vue component files.
- **FR-024**: TypeScript strict mode MUST be enabled; `any` type usage in DTO interface files is prohibited.
- **FR-025**: Tailwind CSS MUST be the sole styling mechanism; no external CSS frameworks or inline `style` attributes for static styling are permitted.

### Key Entities

- **SearchSession**: Represents an active hotel search lifecycle. Key attributes: `sessionId`, `searchKey`, `cacheKey`, `autoSuggestId`, `pollIteration`, `pollStatus`, `searchParams` (destination, dates, rooms), stored in Redis.
- **SearchHistoryRecord**: A persistent log of a search event. Key attributes: `id`, `sessionId`, `destination`, `destinationType`, `checkIn`, `checkOut`, `adultCount`, `childCount`, `roomCount`, `createdAt`. Stored in MySQL via Flyway migration.
- **HotelCard**: Frontend representation of a hotel from poll results. Key attributes mirror the documented hotel payload: `hotelId`, `hotelName`, `city`, `rating`, `price`, `currency`, `availableRooms`.
- **ConversationalTurn**: A single exchange in the chat interface. Key attributes: `role` (user/assistant), `content`, `timestamp`, `sessionId`. Stored in Redis conversational memory.

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A user can issue a natural-language hotel search and see the first batch of hotel results appear within 5 seconds of query submission.
- **SC-002**: Hotel results are progressively rendered during the poll loop — users see hotels populating in real time rather than waiting for a single bulk result.
- **SC-003**: The complete end-to-end search-to-room-selection flow (search → progressive results → hotel detail → room list) is completable without page reload.
- **SC-004**: Token expiry during an active session is recovered invisibly — the user experiences no interruption and receives no token-related error message.
- **SC-005**: Search history records are written for 100% of completed hotel searches, with zero blocking impact on the search response time.
- **SC-006**: All four async states (loading, partial, empty, error) are correctly rendered for every API-backed screen, with no blank or unhandled states reachable by a user.
- **SC-007**: The full local development stack (infrastructure + AI service + frontend) is launchable with no more than 3 commands (one per layer), and all three layers start successfully on both macOS and Windows.
- **SC-008**: A polling loop that does not complete within 60 seconds terminates cleanly, displays any partial results already received, and shows a clear timeout message — no infinite loading states.

---

## Assumptions

- Users are authenticated at the session level via the NexTrip AI application; individual user accounts and login are out of scope for this feature.
- The Spring Boot wrapper APIs are available and reachable at the `HOTEL_API_BASE_URL` environment variable value during development and production.
- Redis 7.x and MySQL 8.x are available via Docker Compose for local development; no cloud-managed database services are required for MVP.
- For MVP, one room with one adult guest is treated as the default room configuration when the user does not specify room/guest details in their search query.
- The `filterBySupplier` field on Room Details requests is always sent as an empty array `[]` for MVP; supplier filtering is a future-scope item.
- External PG redirection is a URL handoff only — NexTrip AI does not process payment responses, handle webhooks, or confirm bookings in the MVP.
- Flyway migration files will be authored as part of MVP delivery for the `search_history` table; no pre-existing schema exists.
- OpenAI SDK is used for LLM-powered conversational understanding; the specific model variant (e.g., GPT-4o) is configurable via environment variable and is not hardcoded.
- Redis serves dual purpose: conversational memory (session turns) and polling state (searchKey/cacheKey/autoSuggestId) — both are keyed by session ID and namespaced to allow future RAG embedding storage.

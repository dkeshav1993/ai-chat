# Research: AI-Powered Hotel Discovery Platform (NexTrip AI)

**Phase**: 0 — Unknowns Resolution
**Date**: 2026-05-23
**Feature**: [spec.md](./spec.md) | [plan.md](./plan.md)

---

## 1. LangGraph StateGraph for Polling Orchestration

**Decision**: Use LangGraph `StateGraph` with typed `TypedDict` state. Each polling iteration is a conditional edge (loop back to `poll_background_status` while `inProgress` is true; continue to `fetch_poll_results` when false or timeout).

**Rationale**: LangGraph's graph model naturally maps to the polling lifecycle sequence (AutoSuggest → Search → poll loop → stream). Conditional edges handle the loop cleanly without recursive calls. State is passed through all nodes, making `searchKey`/`cacheKey`/`autoSuggestId` available to every node without global state.

**Pattern**:
```python
from langgraph.graph import StateGraph, END
from typing import TypedDict, List, Optional

class SearchState(TypedDict):
    session_id: str
    query: str
    destination: str
    check_in: str
    check_out: str
    rooms: list
    auto_suggest_id: Optional[str]
    autosuggest_identifier: Optional[dict]
    search_key: Optional[str]
    cache_key: Optional[str]
    poll_iteration: int
    poll_start_time: float
    hotels: List[dict]
    is_complete: bool
    error: Optional[dict]

graph = StateGraph(SearchState)
graph.add_node("extract_intent", extract_intent_node)
graph.add_node("autosuggest", autosuggest_node)
graph.add_node("trigger_search", trigger_search_node)
graph.add_node("poll_background_status", poll_background_status_node)
graph.add_node("fetch_poll_results", fetch_poll_results_node)
graph.add_node("write_history", write_history_node)

graph.add_conditional_edges(
    "poll_background_status",
    lambda s: "continue_poll" if s["poll_in_progress"] else "fetch_results",
    {"continue_poll": "poll_background_status", "fetch_results": "fetch_poll_results"}
)
```

**Alternatives considered**:
- Plain `asyncio` loop in a service function: Simpler but does not cleanly support future node insertion (fare-recheck, booking) — violates Principle X.
- LangGraph `MessageGraph`: For chat agents only; not appropriate for a structured multi-step API orchestration flow.

---

## 2. SSE Streaming from FastAPI to Nuxt 3

**Decision**: Use `sse-starlette` (`EventSourceResponse`) for the SSE endpoint. Use the native browser `EventSource` API in the Nuxt 3 composable (no library needed). The SSE endpoint is a `GET` route (required by EventSource spec).

**Rationale**: `sse-starlette` integrates cleanly with FastAPI async generators. The browser's native `EventSource` is sufficient for MVP — no need for `eventsource-parser` or `@microsoft/fetch-event-source` at this stage.

**Pattern (FastAPI)**:
```python
from sse_starlette.sse import EventSourceResponse
import asyncio, json

@router.get("/chat/search")
async def chat_search(session_id: str, query: str):
    async def event_generator():
        async for state in hotel_search_graph.astream({"query": query, "session_id": session_id}):
            if "hotels_batch" in state:
                yield {"event": "hotels_batch", "data": json.dumps(state["hotels_batch"])}
            elif "error" in state:
                yield {"event": "error", "data": json.dumps(state["error"])}
        yield {"event": "search_complete", "data": json.dumps({"status": "done"})}
    return EventSourceResponse(event_generator())
```

**Pattern (Nuxt 3 composable)**:
```typescript
const eventSource = new EventSource(`/api/chat/search?sessionId=${sessionId}&query=${encodeURIComponent(query)}`)
eventSource.addEventListener('hotels_batch', (e) => {
  const batch = JSON.parse(e.data)
  hotels.value.push(...batch.hotels)
})
eventSource.addEventListener('error', (e) => {
  const err = JSON.parse(e.data)
  searchError.value = err
  eventSource.close()
})
eventSource.addEventListener('search_complete', () => {
  isSearchComplete.value = true
  eventSource.close()
})
```

**Alternatives considered**:
- WebSocket: More complex, bidirectional capability not needed for polling results stream.
- Long polling: Simpler but loses progressive rendering capability — violates SC-002.
- `@microsoft/fetch-event-source`: Adds POST capability and retry logic but is over-engineered for MVP.

---

## 3. Token Refresh Strategy

**Decision**: `token_service.py` is a singleton module used by all `*_service.py` files. Token stored in Redis with TTL. On 401 / `"token expired"` message: refresh once, retry the failed call once. No global `httpx` middleware interceptor — keep it explicit.

**Rationale**: A shared singleton avoids duplicate token-refresh code across 6 service files (Principle IV). Explicit call-site retry (not middleware) keeps the retry logic visible and debuggable. Redis TTL auto-expires the token so the next `get_token()` miss triggers a fresh fetch.

**Pattern**:
```python
class TokenService:
    def __init__(self, redis: Redis, config: Settings):
        self.redis = redis
        self.config = config
        self.key = "traversia:token"

    async def get_token(self) -> str:
        token = await self.redis.get(self.key)
        if token:
            return token.decode()
        return await self._fetch_and_cache()

    async def _fetch_and_cache(self) -> str:
        resp = await httpx.AsyncClient().post(
            f"{self.config.HOTEL_API_BASE_URL}/authenticationserver/.../generateToken",
            json={"moduleID": self.config.HOTEL_API_MODULE_ID, ...}
        )
        token = resp.json()["token"]
        await self.redis.setex(self.key, 3600, token)  # TTL: 1 hour (adjust to actual expiry)
        return token

    async def refresh_and_retry(self, call: Callable) -> Any:
        await self._fetch_and_cache()  # Force refresh
        return await call()            # Retry once
```

**Token TTL note**: The Token API does not document an explicit expiry period. Default TTL set to 3600 s (1 hour). If the upstream returns an expiry hint in future, the TTL should be updated to match.

**Alternatives considered**:
- `httpx` event hooks / transport middleware for automatic injection: Adds invisible complexity; harder to test and debug.
- Per-service token fetch: Duplicates code, creates race conditions on simultaneous expiry — prohibited by constitution.

---

## 4. Polling Timeout and Cancellation

**Decision**: Track `poll_start_time` (Unix timestamp) in `SearchState`. On each `poll_background_status` node entry, check `time.time() - poll_start_time > POLL_TIMEOUT_SECONDS`. If exceeded, transition to error node and emit `POLL_TIMEOUT` SSE event. For concurrent search (new query while poll active): `useHotelSearch.ts` closes the previous `EventSource` before opening a new one; Redis poll state is overwritten by the new search.

**Rationale**: Time-based timeout in state is the simplest approach compatible with LangGraph's synchronous state transitions. Redis key overwrite is safe because each user has one active search at a time (MVP scope).

**Alternatives considered**:
- `asyncio.wait_for` wrapping the entire graph: Kills the entire coroutine without emitting a terminal SSE event — violates Principle VII (no silent close).
- Separate `asyncio.Task` with `task.cancel()`: Adds concurrency complexity not justified for single-session MVP.

---

## 5. Async MySQL Writes (Search History)

**Decision**: Use `aiomysql` connection pool. `history_service.write_search_history()` is called via `asyncio.create_task()` inside the LangGraph `write_history` node — fire and forget. Exceptions are caught inside the task and logged; never propagated to the search flow.

**Pattern**:
```python
async def write_search_history_task(record: SearchHistoryRecord, pool):
    try:
        async with pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(INSERT_SQL, record.to_tuple())
                await conn.commit()
    except Exception as e:
        logger.error("search_history_write_failed", error=str(e), session_id=record.session_id)

# In LangGraph node:
asyncio.create_task(write_search_history_task(record, db_pool))
```

**Alternatives considered**:
- `await` the write directly: Adds DB latency to the search critical path — violates SC-005.
- Background queue (Redis pub/sub, Celery): Over-engineered for a single write per search.

---

## 6. Flyway Migration Strategy

**Decision**: Flyway CLI run as Docker Compose service (`flyway` image) with `depends_on: mysql`. Migrations in `db/migrations/`. Only versioned migrations (`V{n}__description.sql`) — no repeatable migrations for MVP.

**Pattern (docker-compose.yml)**:
```yaml
flyway:
  image: flyway/flyway:latest
  command: -url=jdbc:mysql://mysql:3306/traversia -user=${MYSQL_USER} -password=${MYSQL_PASSWORD} migrate
  volumes:
    - ./db/migrations:/flyway/sql
  depends_on:
    mysql:
      condition: service_healthy
```

**Rationale**: Running Flyway as a Docker Compose service means migrations run automatically on `docker compose up` — no manual step required. Satisfies Principle IX (single-command startup).

**Alternatives considered**:
- Flyway Maven plugin: Requires Java on the host — breaks cross-platform compatibility.
- Alembic (Python): Appropriate for pure-Python stacks; using Flyway keeps the DB migration story consistent with the Spring Boot layer's conventions.

---

## 7. Nuxt 3 Composables Architecture

**Decision**: Four primary composables. Each composable owns one capability slice. No business logic in `.vue` files — only reactive bindings and event handlers that call composable methods.

| Composable | Owns |
|---|---|
| `useHotelSearch` | EventSource lifecycle, hotel card accumulation, search state machine (idle / searching / streaming / complete / error) |
| `useHotelDetails` | Hotel detail fetch, four async states |
| `useRoomDetails` | Room detail fetch, four async states, PG redirect trigger |
| `useChat` | Conversational turn array, send message action |

**Pattern (useHotelSearch.ts)**:
```typescript
export function useHotelSearch() {
  const hotels = ref<HotelCard[]>([])
  const searchState = ref<'idle' | 'searching' | 'streaming' | 'complete' | 'error'>('idle')
  const searchError = ref<SseErrorEvent | null>(null)
  let eventSource: EventSource | null = null

  function startSearch(query: string, sessionId: string) {
    eventSource?.close()  // Cancel any active search
    hotels.value = []
    searchState.value = 'searching'
    eventSource = new EventSource(`/api/chat/search?sessionId=${sessionId}&query=${encodeURIComponent(query)}`)
    // ... event listeners
  }

  return { hotels, searchState, searchError, startSearch }
}
```

**Alternatives considered**:
- Pinia store for search state: Adds a global store for state that is inherently scoped to a single page. Unnecessary complexity.
- Axios with polling on the frontend: Violates Principle VIII (frontend must not drive polling).

---

## 8. Redis Key Namespace Design

**Decision**: All Redis keys use the prefix `traversia:` with sub-namespaces:

| Key | Type | TTL | Content |
|---|---|---|---|
| `traversia:token` | String | 3600 s | Bearer token string |
| `traversia:session:{sessionId}:memory` | List | 86400 s | JSON-serialised chat turns |
| `traversia:session:{sessionId}:poll` | Hash | 86400 s | `searchKey`, `cacheKey`, `autoSuggestId`, `pollIteration`, `pollStartTime` |

**Rationale**: Namespaced keys allow future addition of `traversia:session:{sessionId}:embeddings` (RAG, Principle X) and `traversia:session:{sessionId}:traveller` (booking flow) without collision.

---

## 9. correlationId Generation

**Decision**: Generated as UUID v4 in TypeScript (`utils/correlationId.ts` using `crypto.randomUUID()`) for requests originating from the frontend → AI service. For requests originating within the AI service (direct calls not triggered by frontend), generated in Python (`uuid.uuid4()`). The correlationId from the original user request is threaded through all downstream Spring Boot calls made during that request's lifecycle.

**Rationale**: `crypto.randomUUID()` is available natively in modern browsers and Node.js — no library dependency needed.

---

## Resolved Unknowns Summary

| Unknown | Resolution |
|---|---|
| LangGraph polling loop pattern | StateGraph with conditional edge loop; timeout via state timestamp |
| SSE library choice | `sse-starlette` (FastAPI), native `EventSource` (frontend) |
| Token TTL | 3600 s default; configurable if upstream expiry is documented |
| Async DB write pattern | `asyncio.create_task()` fire-and-forget |
| Flyway execution | Docker Compose `flyway` service — auto-runs on `docker compose up` |
| Redis namespacing | `traversia:session:{sessionId}:{scope}` — extensible for RAG/booking |
| Poll timeout mechanism | State timestamp checked on each node entry |
| Concurrent search | Frontend closes previous EventSource; Redis poll state overwritten |

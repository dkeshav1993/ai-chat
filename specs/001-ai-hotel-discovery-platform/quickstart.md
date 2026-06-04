# Quickstart: NexTrip AI Local Development

**Date**: 2026-05-23
**Platform**: macOS / Windows
**Estimated time to first running search**: ~15 minutes from clone

---

## Prerequisites

| Tool | Version | Install |
|---|---|---|
| Docker Desktop | Latest | https://docs.docker.com/get-docker/ |
| Node.js | 20 LTS | https://nodejs.org or `nvm install 20` |
| Python | 3.11+ | https://python.org or `pyenv install 3.11` |
| Git | Any | Pre-installed on macOS; Git for Windows on Windows |

No other system-level services required. Redis and MySQL run in Docker.

---

## Step 1 — Clone and Configure

```bash
git clone <repo-url>
cd ai-chat
cp .env.example .env
```

Open `.env` and fill in:
- `OPENAI_API_KEY` — your OpenAI API key
- All other values are pre-filled with local Docker defaults and work out of the box

---

## Step 2 — Start Infrastructure (Redis + MySQL + Flyway)

```bash
docker compose up -d
```

This starts:
- **MySQL 8** on `localhost:3306` (database: `traversia`, user: `traversia`, password: `traversia_local`)
- **Redis 7** on `localhost:6379`
- **Flyway** runs automatically, applies `V1__create_search_history.sql`, then exits

Verify everything is healthy:
```bash
docker compose ps
# mysql and redis should show "healthy"; flyway shows "exited (0)"
```

---

## Step 3 — Start the AI Service (FastAPI)

```bash
cd ai-service
python -m venv .venv

# macOS / Linux:
source .venv/bin/activate

# Windows (PowerShell):
.venv\Scripts\Activate.ps1

pip install -r requirements.txt

# Run from inside ai-service/ directory:
uvicorn main:app --reload --port 8000
```

Verify:
```bash
curl http://localhost:8000/health
# → {"status": "ok"}
```

---

## Step 4 — Start the Frontend (Nuxt 3)

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:3000

---

## Step 5 — Test a Search

In the chat interface, type:
```
Find me a hotel in Mumbai from 20 October to 25 October for 2 adults
```

You should see:
1. A "thinking" message appear in the chat
2. Hotel cards progressively loading
3. A "Search complete" status when the poll loop finishes

---

## Environment Variables Reference

All variables are documented in `.env.example`. Here is a summary:

```env
# Spring Boot wrapper (do not change for dev — uses live API)
HOTEL_API_BASE_URL=https://travelonedev-services.thomascook.in
HOTEL_API_MODULE_ID=Traversia
HOTEL_API_USERNAME=traversia
HOTEL_API_PASSWORD=Traversia@123

# Redis (Docker default)
REDIS_URL=redis://localhost:6379

# MySQL (Docker default — match docker-compose.yml)
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_DB=traversia
MYSQL_USER=traversia
MYSQL_PASSWORD=traversia_local

# OpenAI
OPENAI_API_KEY=sk-YOUR_KEY_HERE
OPENAI_MODEL=gpt-4o

# Polling
POLL_TIMEOUT_SECONDS=60
POLL_INTERVAL_SECONDS=2
```

---

## Docker Compose Reference

```yaml
# docker-compose.yml (summary)
services:
  mysql:
    image: mysql:8.0
    environment:
      MYSQL_DATABASE: traversia
      MYSQL_USER: traversia
      MYSQL_PASSWORD: traversia_local
      MYSQL_ROOT_PASSWORD: root_local
    ports:
      - "3306:3306"
    healthcheck:
      test: ["CMD", "mysqladmin", "ping", "-h", "localhost"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s

  flyway:
    image: flyway/flyway:latest
    command: >
      -url=jdbc:mysql://mysql:3306/traversia
      -user=traversia
      -password=traversia_local
      -connectRetries=5
      migrate
    volumes:
      - ./db/migrations:/flyway/sql
    depends_on:
      mysql:
        condition: service_healthy
```

---

## Troubleshooting

**MySQL connection refused**
- Docker Desktop may need a moment to start. Run `docker compose ps` and wait for `mysql` to show `healthy`.

**Flyway migration failed**
- Check `docker compose logs flyway`. Most common cause: MySQL not ready yet.
- Fix: `docker compose restart flyway`
- Verify the `search_history` table was created:
  ```bash
  docker exec -it traversia_mysql mysql -utraversia -ptraversia_local traversia -e "DESCRIBE search_history;"
  ```

**Token API errors on first search**
- Verify the Spring Boot API is reachable:
  ```bash
  curl -X POST https://travelonedev-services.thomascook.in/authenticationserver/authenticationService/generateToken \
    -H "Content-Type: application/json" \
    -d '{"moduleID":"Traversia","userName":"traversia","password":"Traversia@123"}'
  ```
- Expected: JSON with `token` field and `tokenValid: true`.

**SSE stream not connecting**
- Verify FastAPI is running on port 8000: `curl http://localhost:8000/health`
- Verify Nuxt proxy is configured in `nuxt.config.ts` under `nitro.devProxy`

**Windows path issues**
- Use PowerShell (not cmd). Docker Desktop must have WSL 2 backend enabled.
- If `source .venv/bin/activate` fails, use `.venv\Scripts\Activate.ps1` instead.

---

## End-to-End Local Validation

Complete this checklist to confirm the full stack is working:

### 1. Infrastructure Health
```bash
docker compose ps
# Expected: mysql → healthy, redis → healthy, flyway → exited (0)
```

### 2. Database Migration
```bash
docker exec -it traversia_mysql mysql -utraversia -ptraversia_local traversia \
  -e "SHOW TABLES; DESCRIBE search_history;"
# Expected: search_history table with all columns visible
```

### 3. AI Service Health
```bash
curl http://localhost:8000/health
# Expected: {"status": "ok"}
```

### 4. Token Pre-fetch (check AI service logs)
On startup the AI service logs:
```
startup_token_fetch_success token_length=...
```

### 5. Redis Token Cache
```bash
# Check Redis has the token cached:
docker exec -it traversia_redis redis-cli get traversia:token
# Expected: a JWT string (not nil)
```

### 6. AutoSuggest API via FastAPI (smoke test)
```bash
# Not directly exposed — trigger via the chat SSE endpoint:
curl "http://localhost:8000/chat/search?session_id=test123&query=hotels+in+Mumbai" \
  --no-buffer -H "Accept: text/event-stream"
# Expected: stream of SSE events starting with "event: thinking"
```

### 7. Frontend Search Flow
1. Open http://localhost:3000
2. Type: `Find me a hotel in Mumbai from 20 Oct to 23 Oct for 2 adults`
3. Verify: thinking message appears, hotel cards load progressively
4. Verify: "Found N hotels" bubble appears when search completes

### 8. Hotel Details
1. Click "View Details" on any hotel card
2. Verify: hotel detail page loads at `/hotels/{hotelId}`
3. Verify: "View Available Rooms" button is visible

### 9. Room Details
1. Click "View Available Rooms"
2. Verify: room list loads at `/hotels/{hotelId}/rooms`
3. Click "Select Room" — verify new tab opens with PG redirect URL

### 10. Search History in MySQL
After a successful search:
```bash
docker exec -it traversia_mysql mysql -utraversia -ptraversia_local traversia \
  -e "SELECT session_id, destination, check_in, check_out, created_at FROM search_history ORDER BY created_at DESC LIMIT 5;"
# Expected: row(s) visible with your search destination and dates
```

---

## One-Page Startup Cheatsheet

```bash
# Terminal 1 — Infrastructure
docker compose up -d

# Terminal 2 — AI Service
cd ai-service && source .venv/bin/activate && uvicorn main:app --reload --port 8000

# Terminal 3 — Frontend
cd frontend && npm run dev
```

Open http://localhost:3000 → start searching.

# Mock Provider Strategy

The system must support both:

* real API provider
* mock API provider

The provider implementation must be switchable using environment variables.

Example:

USE_MOCK_PROVIDER=true

---

# Purpose

Mock provider exists to support:

* local development
* offline development
* backend downtime
* frontend integration
* AI orchestration testing
* QA testing
* demo environments

---

# Critical Rules

Mock APIs must:

* strictly follow real API contracts
* use identical DTOs
* preserve request/response structure
* preserve error structures
* preserve polling lifecycle
* preserve token lifecycle

Do NOT generate simplified mock DTOs.

---

# Mock Data Requirements

Mock data must support:

* Delhi
* Goa
* Mumbai
* Dubai
* Bangkok

Each destination should include:

* auto suggest responses
* search responses
* polling responses
* hotel details
* room details

---

# Polling Simulation

The mock provider must simulate progressive polling.

Example:

* first poll returns 2 hotels
* second poll returns 5 hotels
* third poll returns 15 hotels

The frontend should behave identically for:

* real APIs
* mock APIs

---

# Latency Simulation

Mock APIs must simulate realistic latency.

Examples:

* auto suggest → 200ms
* search → 1 second
* poll → 2 seconds

---

# Failure Simulation

The mock provider must support configurable scenarios:

MOCK_SCENARIO=success
MOCK_SCENARIO=timeout
MOCK_SCENARIO=empty
MOCK_SCENARIO=downstream_error

This is required for frontend resilience testing.

---

# Folder Structure

mock-data/
autosuggest/
search/
poll/
hotel-details/
room-details/

---

# Provider Architecture

Create:

* provider interface
* real provider implementation
* mock provider implementation
* provider factory

Environment switching:

USE_MOCK_PROVIDER=true/false

---

# Important

Frontend components must NEVER contain hardcoded mock JSON.

All mock responses must originate from provider implementations only.

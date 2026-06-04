# Hotel Search Flow

## Search Lifecycle

The hotel search flow is asynchronous and polling based.

Flow:

1. User enters destination
2. Auto Suggest API returns destination identifiers
3. Search API triggers downstream vendor search
4. Search API returns:

   * searchKey
   * cacheKey
5. Background Process Status API checks vendor completion state
6. Search By Poll API progressively fetches hotel results
7. Frontend progressively renders hotels while polling continues

---

## Important Rules

* hotel results are incremental
* polling continues until processing completes
* frontend must support progressive loading
* searchKey and cacheKey are mandatory lifecycle identifiers

---

## Authentication

* all APIs require bearer token
* token API generates access token
* token expiry should automatically trigger token regeneration
* failed request retries once after token refresh

---

## MVP Scope

Included:

* conversational hotel search
* hotel listing
* hotel details
* room details
* search history logging
* external PG redirection

Excluded:

* booking confirmation
* fare recheck
* payment execution
* vouchers
* cancellation flows

---

## Future Scope

Architecture must support:

* fare recheck
* traveller forms
* booking APIs
* payment orchestration
* vouchers
* AI recommendations
* multilingual support
* voice AI

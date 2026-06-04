import { ref, computed } from 'vue'
import type { HotelCard } from '~/types/search'
import type {
  SearchState,
  SseErrorEvent,
  SseHotelsBatchEvent,
  SseInitialHotelsEvent,
  SseCuratedReadyEvent,
  SseThinkingEvent,
  SseSearchCompleteEvent,
  SseClarificationNeededEvent,
} from '~/types/sse'

export interface ActiveFilters {
  hotelName?: string | null
  starRating?: number | null
  starRatings?: number[] | null  // multi-select star ratings
  budgetMin?: number | null
  budgetMax?: number | null
}

// ─── Client-side filter logic (mirrors backend _apply_filters) ────────────────
function applyClientFilters(hotels: HotelCard[], filters: ActiveFilters): HotelCard[] {
  let result = hotels

  const nameFilter = (filters.hotelName || '').trim().toLowerCase()
  if (nameFilter) {
    result = result.filter(h => (h.name || '').toLowerCase().includes(nameFilter))
  }

  // Multi-select star rating: starRatings takes precedence over starRating
  const stars = filters.starRatings?.length ? filters.starRatings : (filters.starRating ? [filters.starRating] : [])
  if (stars.length > 0) {
    result = result.filter(h => {
      const raw = (h as any).starRating || (h as any).rating || ''
      try { return stars.includes(Math.floor(parseFloat(String(raw)))) }
      catch { return false }
    })
  }

  if (filters.budgetMin != null || filters.budgetMax != null) {
    result = result.filter(h => {
      const providers: any[] = (h as any).providerInfo || []
      if (!providers.length) return true
      const fares = providers
        .filter(p => p?.totalFare != null)
        .map(p => parseFloat(p.totalFare))
        .filter(f => !isNaN(f))
      if (!fares.length) return true
      const minFare = Math.min(...fares)
      if (filters.budgetMin != null && minFare < filters.budgetMin) return false
      if (filters.budgetMax != null && minFare > filters.budgetMax) return false
      return true
    })
  }

  return result
}

const _HOTELS_KEY = 'nextrip:hotels'
const _STATE_KEY = 'nextrip:searchState'

function _loadHotels(): HotelCard[] {
  if (typeof window === 'undefined') return []
  try {
    const raw = sessionStorage.getItem(_HOTELS_KEY)
    return raw ? (JSON.parse(raw) as HotelCard[]) : []
  } catch { return [] }
}

function _saveHotels(hotels: HotelCard[]): void {
  if (typeof window === 'undefined') return
  try { sessionStorage.setItem(_HOTELS_KEY, JSON.stringify(hotels)) } catch {}
}

// ─── Singleton search state ───────────────────────────────────────────────────
const _hotels = ref<HotelCard[]>([])          // populated via rehydrateFromSession on client
const _searchState = ref<SearchState>('complete')
const _searchError = ref<SseErrorEvent | null>(null)
const _thinkingMessage = ref<string>('')
const _searchKey = ref<string>('')
const _autoSuggestId = ref<string>('')
const _pendingCurated = ref(false)
const _curatedMessage = ref('')
const _curatedSessionId = ref('')
const _loadingCurated = ref(false)
const _clarificationNeeded = ref(false)
const _clarificationMessage = ref('')
const _clarificationMissingFields = ref<string[]>([])
const _activeFilters = ref<ActiveFilters>({})
const _earlyZeroResults = ref(false)
let _eventSource: EventSource | null = null
let _rehydrated = false

export function useHotelSearch() {
  const hotels = _hotels
  const searchState = _searchState
  const searchError = _searchError
  const thinkingMessage = _thinkingMessage
  const searchKey = _searchKey
  const autoSuggestId = _autoSuggestId
  const pendingCurated = _pendingCurated
  const curatedMessage = _curatedMessage
  const curatedSessionId = _curatedSessionId
  const loadingCurated = _loadingCurated
  const clarificationNeeded = _clarificationNeeded
  const clarificationMessage = _clarificationMessage
  const clarificationMissingFields = _clarificationMissingFields
  const activeFilters = _activeFilters
  const earlyZeroResults = _earlyZeroResults

  // Computed filtered list for display
  const filteredHotels = computed(() => {
    if (!hotels.value.length) return []
    const f = activeFilters.value
    const hasAny = !!(f.hotelName || f.starRating || f.budgetMin || f.budgetMax)
    return hasAny ? applyClientFilters(hotels.value, f) : hotels.value
  })

  function cancelSearch(): void {
    if (_eventSource) {
      _eventSource.close()
      _eventSource = null
    }
  }

  function resetState(): void {
    hotels.value = []
    _saveHotels([])
    searchState.value = 'idle'
    searchError.value = null
    thinkingMessage.value = ''
    searchKey.value = ''
    autoSuggestId.value = ''
    pendingCurated.value = false
    curatedMessage.value = ''
    curatedSessionId.value = ''
    loadingCurated.value = false
    clarificationNeeded.value = false
    clarificationMessage.value = ''
    clarificationMissingFields.value = []
    earlyZeroResults.value = false
    // Keep activeFilters — user may want filters to persist across re-searches
  }

  function setFilters(filters: ActiveFilters): void {
    activeFilters.value = { ...filters }
  }

  function clearFilters(): void {
    activeFilters.value = {}
  }

  // Auto-set filters from query text (called by index.vue after extract_intent)
  function setFiltersFromQuery(filters: ActiveFilters): void {
    // Merge with any manually set filters; query-extracted ones take priority
    activeFilters.value = {
      ...activeFilters.value,
      ...Object.fromEntries(Object.entries(filters).filter(([, v]) => v != null)),
    }
  }

  const hasFilters = computed(() =>
    !!(activeFilters.value.hotelName || activeFilters.value.starRating ||
       (activeFilters.value.starRatings?.length) ||
       activeFilters.value.budgetMin || activeFilters.value.budgetMax)
  )

  function startSearch(query: string, sessionId: string): void {
    cancelSearch()
    resetState()

    searchState.value = 'searching'

    const params = new URLSearchParams({ session_id: sessionId, query })
    const url = `/api/chat/search?${params.toString()}`

    _eventSource = new EventSource(url)

    _eventSource.addEventListener('thinking', (e: MessageEvent) => {
      const data = JSON.parse(e.data) as SseThinkingEvent
      thinkingMessage.value = data.message
    })

    _eventSource.addEventListener('clarification_needed', (e: MessageEvent) => {
      const data = JSON.parse(e.data) as SseClarificationNeededEvent
      clarificationNeeded.value = true
      clarificationMessage.value = data.message
      clarificationMissingFields.value = data.missing_fields || []
      if (data.hotel_name_filter) {
        activeFilters.value = { ...activeFilters.value, hotelName: data.hotel_name_filter }
      }
      searchState.value = 'idle'
      cancelSearch()
    })

    _eventSource.addEventListener('initial_hotels', (e: MessageEvent) => {
      const data = JSON.parse(e.data) as SseInitialHotelsEvent
      hotels.value = data.hotels as unknown as HotelCard[]
      _saveHotels(hotels.value)
      // Immediately signal zero results so UI can show curated-scan message NOW
      if (data.hotels.length === 0) {
        earlyZeroResults.value = true
      }
      searchState.value = 'has_results'
    })

    _eventSource.addEventListener('hotels_batch', (e: MessageEvent) => {
      const data = JSON.parse(e.data) as SseHotelsBatchEvent
      // Poll (enriched) results REPLACE the initial hotel/search feed
      hotels.value = data.hotels as unknown as HotelCard[]
      _saveHotels(hotels.value)
      searchState.value = 'has_results'
    })

    _eventSource.addEventListener('curated_ready', (e: MessageEvent) => {
      const data = JSON.parse(e.data) as SseCuratedReadyEvent
      pendingCurated.value = true
      curatedMessage.value = data.message
      curatedSessionId.value = data.sessionId
    })

    _eventSource.addEventListener('search_complete', (e: MessageEvent) => {
      const data = JSON.parse(e.data) as SseSearchCompleteEvent
      searchKey.value = data.searchKey
      autoSuggestId.value = data.autoSuggestId
      searchState.value = 'complete'
      cancelSearch()
    })

    _eventSource.addEventListener('error', (e: MessageEvent) => {
      try {
        const data = JSON.parse(e.data) as SseErrorEvent
        searchError.value = data
      } catch {
        searchError.value = {
          code: 'INTERNAL_ERROR',
          message: 'An unexpected error occurred.',
          recoverable: true,
        }
      }
      searchState.value = 'error'
      cancelSearch()
    })

    _eventSource.onerror = () => {
      if (searchState.value === 'searching' || searchState.value === 'has_results') {
        searchError.value = {
          code: 'INTERNAL_ERROR',
          message: 'Connection to the search service was lost. Please try again.',
          recoverable: true,
        }
        searchState.value = 'error'
        cancelSearch()
      }
    }
  }

  async function loadCuratedFeed(): Promise<void> {
    if (!curatedSessionId.value || loadingCurated.value) return

    loadingCurated.value = true
    try {
      const response = await fetch('/api/chat/curated-feed', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ session_id: curatedSessionId.value }),
      })

      if (!response.ok) {
        const err = await response.json().catch(() => ({}))
        throw new Error(err?.message ?? `HTTP ${response.status}`)
      }

      const data = await response.json()
      if (data.hotels?.length) {
        hotels.value = data.hotels as HotelCard[]
        _saveHotels(hotels.value)
      }
    } catch (e) {
      console.error('[useHotelSearch] curated feed error:', e)
    } finally {
      loadingCurated.value = false
      pendingCurated.value = false
    }
  }

  function dismissCurated(): void {
    pendingCurated.value = false
  }

  function rehydrateFromSession(): void {
    if (_rehydrated || typeof window === 'undefined') return
    _rehydrated = true
    const loaded = _loadHotels()
    if (loaded.length > 0) {
      _hotels.value = loaded
      _searchState.value = 'complete'
    }
  }

  return {
    hotels,
    filteredHotels,
    searchState,
    searchError,
    thinkingMessage,
    searchKey,
    autoSuggestId,
    pendingCurated,
    curatedMessage,
    loadingCurated,
    clarificationNeeded,
    clarificationMessage,
    clarificationMissingFields,
    activeFilters,
    hasFilters,
    earlyZeroResults,
    startSearch,
    cancelSearch,
    setFilters,
    setFiltersFromQuery,
    clearFilters,
    loadCuratedFeed,
    dismissCurated,
    resetState,
    rehydrateFromSession,
  }
}

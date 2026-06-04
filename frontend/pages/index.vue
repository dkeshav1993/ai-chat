<script setup lang="ts">
import { useHotelSearch } from '~/composables/useHotelSearch'
import { useChat, clearChatSession } from '~/composables/useChat'
import { useSessionId, resetSessionId } from '~/composables/useSessionId'

// ─── Session ──────────────────────────────────────────────────────────────────
const sessionId = ref('')
onMounted(() => { sessionId.value = useSessionId() })

// ─── Hotel search composable ──────────────────────────────────────────────────
const {
  hotels,
  filteredHotels,
  searchState,
  searchError,
  thinkingMessage,
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
} = useHotelSearch()

const { turns, addUserTurn, addAssistantTurn, addThinkingTurn, clearThinking } = useChat()

// User message history for keyboard arrow navigation in ChatInput
const userHistory = computed(() =>
  turns.value.filter(t => t.role === 'user').map(t => t.content as string)
)

// ─── Weather + Zero-results panel state ──────────────────────────────────────
interface WeatherPanelData {
  city: string; temp_C: string; feelsLike_C: string; humidity: string
  weatherDesc: string; weatherIconUrl?: string; windspeedKmph: string
  winddir16Point?: string; uvIndex: string; visibility: string
  cloudcover: string; pressure?: string; precipMM?: string
}
const currentDestination = ref<string | null>(null)
const weatherPanelData = ref<WeatherPanelData | null>(null)
const showWeatherPanel = ref(false)
const isAutoScanningCurated = ref(false)
const nearbyCities = ref<Array<{ name: string; country: string; distance_km: number }>>([])
const showNearbyCities = ref(false)
const curatedAlsoEmpty = ref(false)

async function fetchWeatherForPanel(city: string): Promise<void> {
  try {
    const res = await fetch(`/api/chat/weather?city=${encodeURIComponent(city)}`)
    if (!res.ok) return
    const data = await res.json()
    if (!data.temp_C) return
    weatherPanelData.value = data
    showWeatherPanel.value = true
  } catch { /* non-critical */ }
}

async function fetchNearbyCitiesData(city: string): Promise<void> {
  try {
    const res = await fetch(`/api/chat/nearby?city=${encodeURIComponent(city)}`)
    if (!res.ok) return
    const data = await res.json()
    if (data.nearby && data.nearby.length > 0) {
      nearbyCities.value = data.nearby
      showNearbyCities.value = true
      const cityList = data.nearby.slice(0, 4).map((c: any) => `**${c.name}**`).join(', ')
      addAssistantTurn(
        `🗺️ No hotels found — but here are some nearby cities you might love: ${cityList}. Click one to search there! ✨`
      )
    } else {
      addAssistantTurn(
        "😕 No hotels found even in our curated feed. Try adjusting your dates, budget, or destination — I'm here to help!"
      )
    }
  } catch {
    addAssistantTurn(
      "😕 No hotels found for this search. Try adjusting your dates, budget, or destination!"
    )
  }
}

// ─── Zero-results flow (split into two phases for instant feedback) ───────────

// Phase 1: Called immediately when initial_hotels fires with 0 results.
// Shows message + weather card right away — BEFORE polling completes.
function startZeroResultsEarlyPhase(reason: 'no_raw' | 'filters'): void {
  if (isAutoScanningCurated.value) return
  isAutoScanningCurated.value = true
  showNearbyCities.value = false
  curatedAlsoEmpty.value = false

  clearThinking()

  if (reason === 'no_raw') {
    addAssistantTurn(
      `🔍 No hotels found for your search. **Don't worry!** I'm now scanning our curated feed for the best options. This will just take a moment...`
    )
  } else {
    addAssistantTurn(
      `🎯 Your filters are very specific — no results match right now. **Hold on!** I'm scanning our curated feed to find something close for you...`
    )
  }

  // Show weather immediately (fire-and-forget)
  const dest = currentDestination.value
  if (dest) fetchWeatherForPanel(dest)
}

// Phase 2: Called when search_complete fires AND we already started Phase 1.
// Loads the actual curated feed and follows up.
async function finalizeCuratedLoad(): Promise<void> {
  const dest = currentDestination.value
  const filterActive = hasFilters.value
  try {
    await loadCuratedFeed()
    const count = hotels.value.length
    const filtered = filteredHotels.value.length

    if (count > 0) {
      isAutoScanningCurated.value = false
      if (filterActive && filtered < count) {
        addAssistantTurn(
          `✨ Deep-dived into our curated inventory! Found **${count} hotel${count !== 1 ? 's' : ''}** — **${filtered}** match your filters perfectly. Check them out on the right! 🏨`
        )
      } else if (filterActive && filtered === 0) {
        addAssistantTurn(
          `✨ Scanned the curated inventory! Found **${count} hotel${count !== 1 ? 's' : ''}**, though none match your exact filters. Showing all of them so you can pick your favourite! 🏨`
        )
        clearFilters()
      } else {
        addAssistantTurn(
          `✨ Great news! Found **${count} curated hotel${count !== 1 ? 's' : ''}** for you. Check them out on the right! 🏨`
        )
      }
    } else {
      curatedAlsoEmpty.value = true
      isAutoScanningCurated.value = false
      const filterHint = filterActive ? ' Try removing filters or ' : ' '
      addAssistantTurn(
        `😕 Our curated feed doesn't have matching hotels either.${filterHint}${dest ? "Let me suggest some nearby cities..." : "Try adjusting your search!"}`
      )
      if (dest) await fetchNearbyCitiesData(dest)
    }
  } catch {
    isAutoScanningCurated.value = false
    addAssistantTurn("⚠️ Had trouble loading curated results. Please try again in a moment.")
  }
}

// Legacy: used for filter-based zero results (filters applied after results arrive)
async function triggerZeroResultsFlow(reason: 'filters'): Promise<void> {
  startZeroResultsEarlyPhase(reason)
  await finalizeCuratedLoad()
}

// ─── Layout flags ─────────────────────────────────────────────────────────────
const isSearching = computed(() => searchState.value === 'searching')
const hasResults = computed(() => hotels.value.length > 0 && searchState.value !== 'error')
// Right panel stays open as long as we have weather data OR hotel results OR error
const showRightPanel = computed(() =>
  hasResults.value || !!weatherPanelData.value || searchState.value === 'error'
)
const isPollingInBackground = computed(() => searchState.value === 'has_results' && !pendingCurated.value)
const resultHeaderText = computed(() => {
  if (weatherPanelData.value && !hasResults.value) return `Weather in ${currentDestination.value || '...'}`
  const total = hotels.value.length
  const shown = filteredHotels.value.length
  // Show filter count prominently: "15 hotels · 3 match your filters"
  const filterSuffix = hasFilters.value && shown < total
    ? ` · ${shown} match your filters`
    : hasFilters.value && shown === total
      ? ` · all match filters`
      : ''
  if (searchState.value === 'searching') return 'Searching...'
  if (searchState.value === 'has_results') return `${total} hotel${total !== 1 ? 's' : ''} found · enriching...${filterSuffix}`
  if (searchState.value === 'complete' || pendingCurated.value) return `${total} hotel${total !== 1 ? 's' : ''} found${filterSuffix}`
  return 'Searching...'
})

// ─── Collapse state ───────────────────────────────────────────────────────────
const chatCollapsed = ref(false)
const resultsCollapsed = ref(false)
const showCollapseHint = ref(false)
let hintTimer: ReturnType<typeof setTimeout> | null = null

// Mutual-exclusion: at least one panel must remain open
function collapseChat() {
  if (!resultsCollapsed.value) chatCollapsed.value = true
}
function collapseResults() {
  if (!chatCollapsed.value) resultsCollapsed.value = true
}
function expandChat() {
  chatCollapsed.value = false
}
function expandResults() {
  resultsCollapsed.value = false
}

watch(showRightPanel, (val) => {
  if (val && !showCollapseHint.value) {
    showCollapseHint.value = true
    hintTimer = setTimeout(() => { showCollapseHint.value = false }, 6000)
  }
})

onBeforeUnmount(() => { if (hintTimer) clearTimeout(hintTimer) })

// ─── Scroll preservation for results panel ───────────────────────────────────
const resultsPanelRef = ref<HTMLElement | null>(null)
let _savedResultsScroll = 0
let _hotelsLengthSnapshot = 0

// When hotel list changes, save current scroll and restore after DOM paint
watch(() => hotels.value.length, (newLen) => {
  if (!resultsPanelRef.value) return
  // Save current position before reactive update repaints
  _savedResultsScroll = resultsPanelRef.value.scrollTop
  _hotelsLengthSnapshot = newLen
  nextTick(() => {
    if (resultsPanelRef.value && _savedResultsScroll > 0) {
      resultsPanelRef.value.scrollTop = _savedResultsScroll
    }
  })
})

// ─── Donna Typing Animation ───────────────────────────────────────────────────
const donnaLines = [
  "Hi! I'm Donna ✨ Your AI-powered hotel discovery companion.",
  "Tell me where you want to stay — city, dates, vibe. I'll handle the rest.",
  "I search thousands of hotels in real time to find your perfect match.",
]
// Longest line used to size the container so it never jumps
const donnaLongestLine = "Tell me where you want to stay — city, dates, vibe. I'll handle the rest."
const donnaLineIndex = ref(0)
const donnaText = ref('')
const donnaCursor = ref(true)
let donnaTypingTimer: ReturnType<typeof setTimeout> | null = null

function typeLine(line: string, onDone: () => void) {
  let i = 0
  function type() {
    if (i <= line.length) {
      donnaText.value = line.slice(0, i)
      i++
      donnaTypingTimer = setTimeout(type, 38)
    } else {
      setTimeout(onDone, 1600)
    }
  }
  type()
}

function startDonnaAnimation() {
  donnaLineIndex.value = 0
  donnaText.value = ''
  function nextLine() {
    const line = donnaLines[donnaLineIndex.value]
    typeLine(line, () => {
      donnaLineIndex.value = (donnaLineIndex.value + 1) % donnaLines.length
      donnaText.value = ''
      nextLine()
    })
  }
  nextLine()
}

onMounted(() => {
  startDonnaAnimation()
  rehydrateFromSession()
})
onBeforeUnmount(() => { if (donnaTypingTimer) clearTimeout(donnaTypingTimer) })

// ─── Suggestions ──────────────────────────────────────────────────────────────
const suggestions = [
  'Find 5 star hotels in dubai between 14 Aug to 16 Aug',
  'Find hotels in Mumbai with a budget of 5000',
  'Show me the best rate of Pullman hotel in Bangkok',
  'Find 3 star Hotels in New Delhi for 01 Dec to 03 Dec',
]

// ─── Additional Info Panel ────────────────────────────────────────────────────
const showAdditionalInfo = ref(false)
const filterHotelName = ref('')
const filterStar = ref<number[]>([])
const filterBudgetMin = ref<number | null>(null)
const filterBudgetMax = ref<number | null>(null)

// Sync panel fields from activeFilters (so panel shows current active filters)
watch(activeFilters, (f) => {
  filterHotelName.value = f.hotelName || ''
  filterStar.value = f.starRatings?.length ? [...f.starRatings] : (f.starRating ? [f.starRating] : [])
  filterBudgetMin.value = f.budgetMin ?? null
  filterBudgetMax.value = f.budgetMax ?? null
}, { deep: true })

function applyAdditionalFilters() {
  setFilters({
    hotelName: filterHotelName.value || null,
    starRatings: filterStar.value.length ? [...filterStar.value] : null,
    starRating: filterStar.value.length === 1 ? filterStar.value[0] : null,
    budgetMin: filterBudgetMin.value,
    budgetMax: filterBudgetMax.value,
  })
  showAdditionalInfo.value = false
  const parts: string[] = []
  if (filterHotelName.value) parts.push(`"${filterHotelName.value}"`)
  if (filterStar.value.length) parts.push(`${filterStar.value.join('★, ')}★`)
  if (filterBudgetMax.value) parts.push(`budget ≤ ₹${filterBudgetMax.value}/night`)
  if (filterBudgetMin.value) parts.push(`budget ≥ ₹${filterBudgetMin.value}/night`)
  addAssistantTurn(
    `Got it! Filtering results${parts.length ? ` — ${parts.join(', ')}` : ''}. Your feed is updated.`
  )
}

function clearAdditionalFilters() {
  filterHotelName.value = ''
  filterStar.value = []
  filterBudgetMin.value = null
  filterBudgetMax.value = null
  clearFilters()
  showAdditionalInfo.value = false
  addAssistantTurn('Filters cleared. Showing all results.')
}

// ─── Filter extraction helpers ────────────────────────────────────────────────
// Extracts all star numbers from query: "3 star and 4 star" → [3, 4]
function extractStarRatings(query: string): number[] {
  const all: number[] = []
  const rx = /(\d)\s*-?\s*star/gi
  let m: RegExpExecArray | null
  while ((m = rx.exec(query)) !== null) {
    const n = parseInt(m[1])
    if (n >= 1 && n <= 5 && !all.includes(n)) all.push(n)
  }
  return all
}
const starRegex = /(\d)\s*-?\s*star/i

// Known hotel brands (extended list)
const brandRegex = /\b(taj|marriott|hilton|hyatt|sheraton|accor|ibis|radisson|westin|intercontinental|holiday inn|courtyard|four seasons|oberoi|leela|itc|novotel|mercure|sofitel|wyndham|ramada|doubletree|pullman|renaissance|fairmont|shangri.la|ritz.?carlton|waldorf|mandarin|banyan|ritz|carlton|crowne|plaza|indigo|lemon tree|oyo|treebo|fabhotel|golden tulip|best western|la quinta|comfort inn|quality inn|days inn|super 8|howard johnson|clarion|sleep inn)\b/i

// Generic adjectives that are NOT hotel names
const _genericHotelAdj = new Set([
  'a','an','the','some','any','good','best','cheap','luxury','budget','nice','great',
  'top','premium','standard','comfortable','affordable','boutique','modern','old','new',
  'famous','beautiful','nice','cheap','economical','expensive','nearest','nearby','local',
  'five','four','three','two','one','star','rated','5','4','3','2','1',
  // Action verbs that should never be treated as hotel names
  'find','search','fetch','extract','get','show','look','book','list','discover',
  'check','browse','see','view','explore','need','want','give','tell','suggest',
])

// Extract hotel name from query text (partial match support)
function extractHotelName(query: string): string | null {
  // 0. Quoted hotel name — highest priority: Hotel "Regency" or 'Regency'
  const quotedM = query.match(/(?:hotel\s+)?["']([^"']{2,40})["']/i)
  if (quotedM) return quotedM[1].trim().toLowerCase()

  // 1. Known brand names
  const brandM = query.match(brandRegex)
  if (brandM) return brandM[1].toLowerCase().replace(/[.\-]/g, '')

  // 2. "hotel name as/is/= X" or "hotel name X"
  const nameAsM = query.match(/\bhotel\s+name\s+(?:as|is|=|:)?\s*([a-z][a-z0-9\s\-]{1,30})/i)
  if (nameAsM) {
    const c = nameAsM[1].trim().toLowerCase().replace(/\s+hotel(s)?$/i, '')
    if (!_genericHotelAdj.has(c) && c.length > 1) return c
  }

  // 3. "filter hotel X" or "apply filter hotel X" — name AFTER the word "hotel"
  const filterHotelM = query.match(/\b(?:filter|apply\s+filter)\s+hotel\s+([a-z][a-z0-9\-]{2,})/i)
  if (filterHotelM) {
    const c = filterHotelM[1].trim().toLowerCase()
    if (!_genericHotelAdj.has(c)) return c
  }

  // 4. "filter/apply filter X hotel" — name BEFORE the word "hotel"
  // Handles: "Filter Regency Hotel", "Apply filter Regency Hotel"
  const filterBeforeHotelM = query.match(/\b(?:filter|apply\s+filter)\s+([a-z][a-z0-9\-]{2,}(?:\s+[a-z][a-z0-9\-]{2,})?)\s+hotels?\b/i)
  if (filterBeforeHotelM) {
    const c = filterBeforeHotelM[1].trim().toLowerCase()
    if (!_genericHotelAdj.has(c) && !/^\d+$/.test(c)) return c
  }

  // 5. "X hotel(s)" pattern — word(s) directly before the word "hotel" (general)
  const beforeHotelM = query.match(/\b([a-z][a-z0-9\-]{2,}(?:\s+[a-z][a-z0-9\-]{2,})?)\s+hotels?\b/i)
  if (beforeHotelM) {
    const c = beforeHotelM[1].trim().toLowerCase()
    if (!_genericHotelAdj.has(c) && !/^\d+$/.test(c)) return c
  }

  // 6. "need/want/show/find/filter + name" — verb followed by candidate word
  // Strips trailing "hotel/hotels" from the captured group to avoid e.g. "regency hotel" as name
  const verbM = query.match(/\b(?:need|want|show|find|filter|looking for|search for|get me|give me)\s+(?:(?:me|a|the|some)\s+)?([a-z][a-z0-9\-]{2,}(?:\s+[a-z][a-z0-9\-]{2,})?)\b(?!\s*(?:in\b|at\b|near\b|from\b|star\b|rated\b|\d|-star))/i)
  if (verbM) {
    const raw = verbM[1].trim().toLowerCase()
    const c = raw.replace(/\s+hotels?$/i, '')  // strip trailing "hotel/hotels"
    if (!_genericHotelAdj.has(c) && !/^(hotel|resort|hostel|villa|room|suite|accommodation|property)/.test(c) && c.length > 1) return c
  }

  return null
}

// Budget extraction — handles many patterns including "budget of X", "max budget of X"
// Returns { max, min, invalidBudget }
function extractBudgetFromText(query: string): { max: number | null; min: number | null; invalidBudget: boolean } {
  // Detect invalid budget: budget-related keyword + non-numeric text where a number is expected
  const invalidBudgetRx = /\b(?:budget|price|cost|spend)\s+(?:of|is|under|max|minimum|above|at most|within)?\s+([a-z]{2,})\b/i
  const invalidM = query.match(invalidBudgetRx)
  if (invalidM && !/\d/.test(invalidM[1])) {
    return { max: null, min: null, invalidBudget: true }
  }

  // Max budget — ordered from most specific to most general
  const maxPatterns = [
    /\b(?:max(?:imum)?\s+)?budget\s+(?:of|is|under|below|max|limit|upto|up to|at most|within)?\s*(?:rs\.?|inr|₹|\$|usd)?\s*([\d,]+)/i,
    /\b(?:under|below|max(?:imum)?|less than|upto|up to|within|at most|not more than)\s+(?:rs\.?|inr|₹|\$|usd)?\s*([\d,]+)/i,
    /\b(?:price|cost|rate|spend|spending)\s+(?:of|is|under|below|max|less than|at most|within)\s+(?:rs\.?|inr|₹|\$|usd)?\s*([\d,]+)/i,
    /(?:rs\.?|inr|₹|\$|usd)\s*([\d,]+)\s*(?:max|budget|limit|per night|a night|\/night)/i,
  ]
  let max: number | null = null
  for (const rx of maxPatterns) {
    const m = query.match(rx)
    if (m) { max = parseFloat(m[1].replace(/,/g, '')); break }
  }

  // Min budget — includes "Min budget is 2000", "Minimum budget is 2000"
  const minPatterns = [
    /\b(?:min(?:imum)?\s+budget|budget\s+min(?:imum)?)\s*(?:is|=|:)?\s*(?:rs\.?|inr|₹|\$|usd)?\s*([\d,]+)/i,
    /\bbudget\s+(?:above|from|minimum|min|more than|over|at least)\s+(?:rs\.?|inr|₹|\$|usd)?\s*([\d,]+)/i,
    /\b(?:from|above|min(?:imum)?|at least|more than|over)\s+(?:rs\.?|inr|₹|\$|usd)?\s*([\d,]+)/i,
  ]
  let min: number | null = null
  for (const rx of minPatterns) {
    const m = query.match(rx)
    if (m) { min = parseFloat(m[1].replace(/,/g, '')); break }
  }

  return { max, min, invalidBudget: false }
}

function extractFiltersFromQuery(query: string): void {
  const extracted: { hotelName?: string | null; starRating?: number | null; starRatings?: number[]; budgetMin?: number | null; budgetMax?: number | null } = {}

  const allStars = extractStarRatings(query)
  if (allStars.length > 0) {
    extracted.starRatings = allStars
    extracted.starRating = allStars.length === 1 ? allStars[0] : allStars[0]
  }

  const hotelName = extractHotelName(query)
  if (hotelName) extracted.hotelName = hotelName

  const budget = extractBudgetFromText(query)
  if (budget.max != null) extracted.budgetMax = budget.max
  if (budget.min != null) extracted.budgetMin = budget.min

  if (Object.keys(extracted).length > 0) {
    setFiltersFromQuery(extracted)
  }
}

// ─── Clear chat ───────────────────────────────────────────────────────────────
function handleClearChat() {
  cancelSearch()
  resetState()
  clearFilters()
  clearChatSession()
  showWeatherPanel.value = false
  weatherPanelData.value = null
  nearbyCities.value = []
  showNearbyCities.value = false
  curatedAlsoEmpty.value = false
  isAutoScanningCurated.value = false
  currentDestination.value = null
  chatCollapsed.value = false
  resultsCollapsed.value = false
  promptStep.value = 'idle'
  pendingSmartFill.value = null
  showAdditionalInfo.value = false
  showClarificationForm.value = false
}

// ─── Checkout date helper ─────────────────────────────────────────────────────
const todayIso = computed(() => new Date().toISOString().split('T')[0])
const checkOutMinDate = computed(() => {
  const ci = clarificationAnswers.value['check_in']
  if (!ci) return ''
  try {
    const d = new Date(ci)
    d.setDate(d.getDate() + 1)
    return d.toISOString().split('T')[0]
  } catch { return '' }
})
const clarificationAnswers = ref<Record<string, string>>({})
const showClarificationForm = ref(false)

watch(clarificationNeeded, (val) => {
  if (val) {
    clearThinking()
    addAssistantTurn(clarificationMessage.value)
    showClarificationForm.value = true
  }
})

function submitClarification() {
  showClarificationForm.value = false
  const dest = clarificationAnswers.value.destination || ''
  const checkIn = clarificationAnswers.value.check_in || ''
  const checkOut = clarificationAnswers.value.check_out || ''
  const adults = clarificationAnswers.value.adults || '1'
  const rooms = clarificationAnswers.value.rooms || '1'

  if (!dest) {
    addAssistantTurn("I still need a destination to search. Could you tell me which city or location you'd like?")
    showClarificationForm.value = true
    return
  }

  const parts: string[] = [`Hotels in ${dest}`]
  if (checkIn) parts.push(`from ${checkIn}`)
  if (checkOut) parts.push(`to ${checkOut}`)
  if (parseInt(adults) > 1) parts.push(`for ${adults} adults`)
  if (parseInt(rooms) > 1) parts.push(`${rooms} rooms`)

  const enrichedQuery = parts.join(' ')
  clarificationAnswers.value = {}
  handleSubmit(enrichedQuery)
}

async function skipClarification() {
  showClarificationForm.value = false
  clarificationAnswers.value = {}
  const tomorrow = _getTomorrow(); const dayAfter = _getDayAfter(tomorrow)
  let city = currentDestination.value || ''

  addAssistantTurn('🌍 Detecting your location...')
  if (process.client && navigator.geolocation) {
    try {
      const pos: GeolocationPosition = await new Promise((resolve, reject) =>
        navigator.geolocation.getCurrentPosition(resolve, reject, { timeout: 6000 })
      )
      const res = await fetch(
        `https://nominatim.openstreetmap.org/reverse?lat=${pos.coords.latitude}&lon=${pos.coords.longitude}&format=json`,
        { headers: { 'Accept-Language': 'en' } }
      )
      if (res.ok) {
        const data = await res.json()
        city = data.address?.city || data.address?.town || data.address?.county || city
      }
    } catch { /* geolocation denied or timed out */ }
  }

  pendingSmartFill.value = { destination: city || undefined, checkIn: tomorrow, checkOut: dayAfter, adults: 1, rooms: 1 }
  promptStep.value = 'skip-geo-offered'

  const cityLine = city ? `📍 City: **${city}**` : '📍 City: *(not detected — please provide)*'
  addAssistantTurn(
    `Here are the smart defaults I can use:\n${cityLine}\n📅 Check-in: **${_fmtDate(tomorrow)}**\n📅 Check-out: **${_fmtDate(dayAfter)}**\n👥 **1 adult**, 1 room\n\nReply **yes** to search with these, or **no** to fill manually.`
  )
}

// ─── Lead form flow ───────────────────────────────────────────────────────────
type LeadStep = 'idle' | 'offered' | 'name' | 'phone' | 'email' | 'done'
const leadStep = ref<LeadStep>('idle')
const leadData = ref({ name: '', phone: '', email: '', query: '' })

function isLeadCapturing() { return leadStep.value !== 'idle' && leadStep.value !== 'done' }

async function submitLead() {
  try {
    await fetch('/api/chat/lead', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(leadData.value),
    })
  } catch { /* silently ignore */ }
  addAssistantTurn("Perfect! 🎉 Our sales team will reach out to you shortly. You can also call us on **1800-2099-100** anytime. Is there anything else I can help you with?")
  leadStep.value = 'done'
  setTimeout(() => { leadStep.value = 'idle' }, 3000)
}

function handleLeadInput(input: string) {
  if (leadStep.value === 'offered') {
    if (/yes|yeah|sure|ok|yep/i.test(input)) {
      leadStep.value = 'name'
      addAssistantTurn("Great! Could you share your **name** please?")
    } else {
      leadStep.value = 'idle'
      addAssistantTurn("No problem! I'm Donna — ready to help with hotel searches whenever you need. 🏨")
    }
    return true
  }
  if (leadStep.value === 'name') {
    leadData.value.name = input
    leadStep.value = 'phone'
    addAssistantTurn(`Thanks ${input}! 😊 What's your **phone number**?`)
    return true
  }
  if (leadStep.value === 'phone') {
    leadData.value.phone = input
    leadStep.value = 'email'
    addAssistantTurn("Almost there! What's your **email address**?")
    return true
  }
  if (leadStep.value === 'email') {
    leadData.value.email = input
    submitLead()
    return true
  }
  return false
}

// ─── Hotel search keywords ────────────────────────────────────────────────────
const hotelKeywords = /hotel|stay|room|resort|hostel|book|check.?in|check.?out|night|guest|suite|accommodation|travel|trip|vacation|holiday/i
const cityPattern = /\b(mumbai|delhi|goa|bangalore|hyderabad|chennai|kolkata|jaipur|agra|pune|dubai|bangkok|singapore|paris|london|new york|bali|phuket|colombo|kathmandu|lahore|karachi|dhaka|islamabad|riyadh|doha|abu dhabi|kuala lumpur)\b/i

function isHotelRelated(query: string): boolean {
  return hotelKeywords.test(query) || cityPattern.test(query)
}

// ─── Weather punchline ────────────────────────────────────────────────────────
const weatherIcons: Record<string, string> = {
  sunny: '☀️', clear: '☀️', cloud: '⛅', overcast: '☁️', rain: '🌧️',
  drizzle: '🌦️', thunder: '⛈️', snow: '❄️', mist: '🌫️', fog: '🌫️', haze: '🌁',
}

function weatherEmoji(desc: string): string {
  const d = desc.toLowerCase()
  for (const [key, emoji] of Object.entries(weatherIcons)) {
    if (d.includes(key)) return emoji
  }
  return '🌡️'
}

async function fetchWeatherPunchline(destination: string) {
  try {
    const res = await fetch(`/api/chat/weather?city=${encodeURIComponent(destination)}`)
    if (!res.ok) return
    const data = await res.json()
    const temp = data.temp_C
    const desc = data.weatherDesc ?? ''
    const humidity = data.humidity
    const uv = data.uvIndex
    const wind = data.windspeedKmph
    if (!temp) return
    const emoji = weatherEmoji(desc)
    const city = destination.charAt(0).toUpperCase() + destination.slice(1)
    const tempNum = parseInt(temp)
    const tempComment = tempNum > 35
      ? "It's quite hot there! Pack light clothing & stay hydrated. 💧"
      : tempNum < 15
        ? "It's chilly — don't forget a jacket! 🧥"
        : "Perfect weather for a great stay! 🌟"
    const punchlines = [
      `${emoji} FYI — ${city} is currently **${temp}°C** with ${desc.toLowerCase()}. Humidity: ${humidity}%, Wind: ${wind} km/h. ${tempComment}`,
      `${emoji} Weather in ${city}: **${temp}°C**, ${desc}. UV index: ${uv}. ${tempComment}`,
    ]
    addAssistantTurn(punchlines[Math.floor(Math.random() * punchlines.length)])
  } catch { /* weather is non-critical */ }
}

function extractDestination(query: string): string | null {
  const m = query.match(cityPattern)
  if (m) return m[0]
  const locMatch = query.match(/\b(?:in|at|near|for)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)/i)
  if (locMatch) return locMatch[1]
  return null
}

// ─── Comprehensive query parser ───────────────────────────────────────────────
interface ExtractedParams {
  destination: string | null; checkIn: string | null; checkOut: string | null
  adults: number | null; rooms: number | null; starRating: number | null; starRatings: number[]
  hotelName: string | null; budgetMin: number | null; budgetMax: number | null
}

const _monthNames3 = ['jan','feb','mar','apr','may','jun','jul','aug','sep','oct','nov','dec']
const _monthNamesFull = ['january','february','march','april','may','june','july','august','september','october','november','december']

function _toISODate(d: Date): string { return d.toISOString().split('T')[0] }

function _parseDateStr(text: string): string | null {
  const t = text.trim().toLowerCase()
  const today = new Date(); today.setHours(0,0,0,0)
  if (/^today$/i.test(t)) return _toISODate(today)
  if (/^tomorrow$/i.test(t)) { const d = new Date(today); d.setDate(d.getDate()+1); return _toISODate(d) }
  if (/next\s+weekend/i.test(t)) {
    const d = new Date(today); const day = d.getDay()
    d.setDate(d.getDate() + (day === 6 ? 7 : 6 - day)); return _toISODate(d)
  }
  if (/next\s+week/i.test(t)) { const d = new Date(today); d.setDate(d.getDate()+7); return _toISODate(d) }
  const isoM = t.match(/^(\d{4}-\d{2}-\d{2})$/)
  if (isoM) { const d = new Date(isoM[1]); if (!isNaN(d.getTime())) return isoM[1] }
  const allM = [..._monthNames3, ..._monthNamesFull]
  const rx1 = new RegExp(`\\b(${allM.join('|')})\\s+(\\d{1,2})\\b`, 'i')
  const m1 = t.match(rx1)
  if (m1) {
    const mi = _monthNames3.indexOf(m1[1].toLowerCase().slice(0,3))
    const day = parseInt(m1[2])
    if (mi >= 0 && day >= 1 && day <= 31) {
      const d = new Date(today.getFullYear(), mi, day)
      if (d < today) d.setFullYear(d.getFullYear()+1)
      return _toISODate(d)
    }
  }
  const rx2 = new RegExp(`\\b(\\d{1,2})\\s+(${allM.join('|')})\\b`, 'i')
  const m2 = t.match(rx2)
  if (m2) {
    const day = parseInt(m2[1]); const mi = _monthNames3.indexOf(m2[2].toLowerCase().slice(0,3))
    if (mi >= 0 && day >= 1 && day <= 31) {
      const d = new Date(today.getFullYear(), mi, day)
      if (d < today) d.setFullYear(d.getFullYear()+1)
      return _toISODate(d)
    }
  }
  return null
}

function extractAllFromQuery(query: string): ExtractedParams {
  const result: ExtractedParams = {
    destination: null, checkIn: null, checkOut: null,
    adults: null, rooms: null, starRating: null, starRatings: [], hotelName: null, budgetMin: null, budgetMax: null,
  }
  const cityM = query.match(cityPattern)
  if (cityM) result.destination = cityM[0]
  else {
    const locM = query.match(/\b(?:in|at|near|to)\s+([A-Za-z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)?)/i)
    if (locM) {
      const cand = locM[1].trim()
      if (!new Set(['a','the','my','your','me','us','any']).has(cand.toLowerCase())) result.destination = cand
    }
  }
  // "from X to Y" date pair
  const ftM = query.match(/\bfrom\s+(.+?)\s+to\s+(.+?)(?:\s+for\s|\s+\d+\s+(?:adult|guest|person|room)|$)/i)
  if (ftM) {
    const ci = _parseDateStr(ftM[1]); const co = _parseDateStr(ftM[2])
    if (ci) result.checkIn = ci; if (co) result.checkOut = co
  }
  if (!result.checkIn) { const m = query.match(/\bcheck.?in\s+(?:on\s+)?(.+?)(?:\s+check.?out|\s+to\s|\s+for\s|$)/i); if (m) result.checkIn = _parseDateStr(m[1]) }
  if (!result.checkOut) { const m = query.match(/\bcheck.?out\s+(?:on\s+)?(.+?)(?:\s+for\s|$)/i); if (m) result.checkOut = _parseDateStr(m[1]) }
  // standalone month-date references
  if (!result.checkIn || !result.checkOut) {
    const allM = [..._monthNames3, ..._monthNamesFull]
    const dateRx = new RegExp(`\\b(?:${allM.join('|')})\\s+\\d{1,2}\\b|\\b\\d{1,2}\\s+(?:${allM.join('|')})\\b`, 'gi')
    const found: string[] = []; let dm: RegExpExecArray | null
    while ((dm = dateRx.exec(query)) !== null) { const p = _parseDateStr(dm[0]); if (p) found.push(p) }
    if (found.length >= 1 && !result.checkIn) result.checkIn = found[0]
    if (found.length >= 2 && !result.checkOut) result.checkOut = found[1]
  }
  // "for X nights" from checkin
  if (result.checkIn && !result.checkOut) {
    const nm = query.match(/\bfor\s+(\d+)\s+nights?\b/i)
    if (nm) { const d = new Date(result.checkIn); d.setDate(d.getDate()+parseInt(nm[1])); result.checkOut = _toISODate(d) }
  }
  // adults / guests
  const adM = query.match(/\b(\d+)\s*(?:adults?|guests?|persons?|people)\b/i)
  if (adM) result.adults = parseInt(adM[1])
  else {
    const forXM = query.match(/\bfor\s+(\d+)\b(?!\s*nights?)/i)
    if (forXM && parseInt(forXM[1]) <= 10) result.adults = parseInt(forXM[1])
  }
  const rmM = query.match(/\b(\d+)\s*rooms?\b/i); if (rmM) result.rooms = parseInt(rmM[1])
  const allStars = extractStarRatings(query)
  result.starRatings = allStars
  result.starRating = allStars.length === 1 ? allStars[0] : (allStars.length > 0 ? allStars[0] : null)
  const hotelName = extractHotelName(query); if (hotelName) result.hotelName = hotelName
  const budget = extractBudgetFromText(query)
  if (budget.max != null) result.budgetMax = budget.max
  if (budget.min != null) result.budgetMin = budget.min
  return result
}

// ─── Date helpers ─────────────────────────────────────────────────────────────
function _getTomorrow(): string { const d = new Date(); d.setDate(d.getDate()+1); return _toISODate(d) }
function _getDayAfter(iso: string): string { const d = new Date(iso); d.setDate(d.getDate()+1); return _toISODate(d) }
function _fmtDate(iso: string): string {
  try { return new Date(iso).toLocaleDateString('en-US', { weekday:'short', month:'short', day:'numeric' }) }
  catch { return iso }
}

// ─── Smart-fill state machine ─────────────────────────────────────────────────
type PromptStep = 'idle' | 'smart-fill-offered' | 'skip-geo-offered'
const promptStep = ref<PromptStep>('idle')
const pendingSmartFill = ref<{
  destination?: string; checkIn: string; checkOut: string; adults: number; rooms: number
  starRating?: number | null; starRatings?: number[]; hotelName?: string | null; budgetMin?: number | null; budgetMax?: number | null
} | null>(null)

// ─── Stored previous search context for DONNA transparency ───────────────────
const prevSearchContext = ref<{
  destination: string; checkIn: string; checkOut: string; adults: number; rooms: number
} | null>(null)

function handlePromptResponse(input: string): void {
  const yes = /\byes\b|\byeah\b|\byep\b|\bsure\b|\bok\b|\bokay\b|\bgo\b|\bproceed\b/i.test(input)
  const no = /\bno\b|\bnope\b|\bnah\b|\bcancel\b|\bchange\b|\bcustom\b/i.test(input)
  if (yes && pendingSmartFill.value) {
    promptStep.value = 'idle'
    const fill = pendingSmartFill.value
    pendingSmartFill.value = null
    _executeSmartFill(fill)
  } else if (no) {
    promptStep.value = 'idle'
    const fill = pendingSmartFill.value
    pendingSmartFill.value = null
    clarificationAnswers.value = fill?.destination ? { destination: fill.destination } : {}
    // Pre-populate dates/guests if available
    if (fill?.checkIn) clarificationAnswers.value['check_in'] = fill.checkIn
    if (fill?.checkOut) clarificationAnswers.value['check_out'] = fill.checkOut
    if (fill?.adults) clarificationAnswers.value['adults'] = String(fill.adults)
    if (fill?.rooms) clarificationAnswers.value['rooms'] = String(fill.rooms)
    // Preserve any add-on filters from the pending fill
    if (fill?.starRatings?.length) setFiltersFromQuery({ starRatings: fill.starRatings, starRating: fill.starRatings[0] })
    else if (fill?.starRating) setFiltersFromQuery({ starRating: fill.starRating })
    if (fill?.hotelName) setFiltersFromQuery({ hotelName: fill.hotelName })
    if (fill?.budgetMin != null) setFiltersFromQuery({ budgetMin: fill.budgetMin })
    if (fill?.budgetMax != null) setFiltersFromQuery({ budgetMax: fill.budgetMax })
    clarificationMissingFields.value = ['destination', 'check_in', 'check_out']
    showClarificationForm.value = true
    addAssistantTurn("No problem! Fill in your preferred details below 👇")
  } else {
    addAssistantTurn("Just reply **yes** to search with the suggested details, or **no** to fill them in manually.")
  }
}

function _executeSmartFill(fill: NonNullable<typeof pendingSmartFill.value>): void {
  if (fill.starRatings?.length) setFiltersFromQuery({ starRatings: fill.starRatings, starRating: fill.starRatings[0] })
  else if (fill.starRating) setFiltersFromQuery({ starRating: fill.starRating })
  if (fill.hotelName) setFiltersFromQuery({ hotelName: fill.hotelName })
  if (fill.budgetMin != null) setFiltersFromQuery({ budgetMin: fill.budgetMin })
  if (fill.budgetMax != null) setFiltersFromQuery({ budgetMax: fill.budgetMax })
  currentDestination.value = fill.destination || null
  if (fill.destination) {
    fetchWeatherForPanel(fill.destination)
    fetchWeatherPunchline(fill.destination)
  }
  const parts = [fill.destination ? `Hotels in ${fill.destination}` : 'Hotels']
  if (fill.checkIn) parts.push(`from ${fill.checkIn}`)
  if (fill.checkOut) parts.push(`to ${fill.checkOut}`)
  parts.push(`for ${fill.adults} adults`)
  if (fill.rooms > 1) parts.push(`${fill.rooms} rooms`)
  _proceedSearch(parts.join(' '))
}

function _proceedSearch(query: string): void {
  addThinkingTurn('Donna is searching for you...')
  resetSessionId(); sessionId.value = useSessionId()
  showWeatherPanel.value = false; weatherPanelData.value = null
  nearbyCities.value = []; showNearbyCities.value = false
  curatedAlsoEmpty.value = false; isAutoScanningCurated.value = false
  startSearch(query, sessionId.value)
}

// ─── Filter-on-existing-feed intent detection ─────────────────────────────────
// Returns true if the query is clearly asking to filter the CURRENT results
// rather than trigger a brand-new search.
function isFilterOnExistingFeed(query: string, extracted: ExtractedParams): boolean {
  if (hotels.value.length === 0) return false
  const hasFilterSignals = (extracted.starRatings?.length ?? 0) > 0 || extracted.starRating !== null || !!extracted.hotelName ||
    extracted.budgetMax !== null || extracted.budgetMin !== null
  if (!hasFilterSignals) return false
  // New dates → definitely a new search
  if (extracted.checkIn || extracted.checkOut) return false
  // New city different from current → new search
  if (extracted.destination && currentDestination.value &&
    extracted.destination.toLowerCase() !== currentDestination.value.toLowerCase()) return false
  // Same city or no city + filter signals + no new dates → filter existing feed
  return true
}

function applyFilterFromChat(query: string, extracted: ExtractedParams): void {
  // Detect invalid budget (alphabets where number expected)
  const budgetCheck = extractBudgetFromText(query)
  if (budgetCheck.invalidBudget) {
    addAssistantTurn("🚫 I'm afraid I can't apply that budget filter — it looks like a word rather than a number. Please specify a numeric budget, like **₹5000** or **max 5000**.")
    return
  }

  const prev = { ...activeFilters.value }
  const newStars = extracted.starRatings?.length ? extracted.starRatings : null
  const prevStars = prev.starRatings?.length ? prev.starRatings : (prev.starRating ? [prev.starRating] : null)
  setFiltersFromQuery({
    starRating: newStars ? newStars[0] : (prev.starRating ?? null),
    starRatings: newStars ?? prevStars ?? null,
    hotelName: extracted.hotelName ?? prev.hotelName ?? null,
    budgetMin: extracted.budgetMin ?? prev.budgetMin ?? null,
    budgetMax: extracted.budgetMax ?? prev.budgetMax ?? null,
  })
  const parts: string[] = []
  const stars = newStars ?? prevStars
  if (stars?.length) parts.push(`${stars.join('★, ')}★ hotels`)
  if (extracted.hotelName) parts.push(`"${extracted.hotelName}"`)
  if (extracted.budgetMax) parts.push(`budget ≤ ₹${extracted.budgetMax.toLocaleString()}`)
  if (extracted.budgetMin) parts.push(`budget ≥ ₹${extracted.budgetMin.toLocaleString()}`)
  const total = hotels.value.length
  // filteredHotels is reactive-computed — read after setFiltersFromQuery to get correct count
  nextTick(() => {
    const count = filteredHotels.value.length
    if (count > 0) {
      addAssistantTurn(
        `🎯 Applied filters: **${parts.join(', ')}**. Showing **${count}** of ${total} hotel${total !== 1 ? 's' : ''} that match. You can see them on the right!`
      )
    } else {
      addAssistantTurn(
        `🎯 Applied filters: **${parts.join(', ')}** — but no hotels in the current list match those criteria. **Scanning our curated inventory now...** ✨`
      )
      // Trigger curated scan for filter-mismatch
      isAutoScanningCurated.value = false
      triggerZeroResultsFlow('filters')
    }
  })
}

// ─── Main submit handler ──────────────────────────────────────────────────────
function handleSubmit(query: string): void {
  addUserTurn(query)

  if (isLeadCapturing() || leadStep.value === 'offered') {
    handleLeadInput(query)
    return
  }

  // Handle smart-fill / skip-geo yes/no responses
  if (promptStep.value !== 'idle') {
    handlePromptResponse(query)
    return
  }

  // ── Detect "change dates/adults/rooms" — user wants to modify existing search context ──
  const isChangingContext = /\b(?:change|update|modify|edit|set)\s+(?:the\s+)?(?:check.?in|check.?out|dates?|adult|guest|room|night|passenger|travell?er)/i.test(query)
    || /\b(?:different|new|other)\s+(?:dates?|check.?in|check.?out|rooms?|adults?|guests?)\b/i.test(query)
  if (isChangingContext && prevSearchContext.value) {
    const ctx = prevSearchContext.value
    clarificationAnswers.value = {
      destination: ctx.destination,
      check_in: ctx.checkIn,
      check_out: ctx.checkOut,
      adults: String(ctx.adults),
      rooms: String(ctx.rooms),
    }
    clarificationMissingFields.value = ['destination', 'check_in', 'check_out']
    showClarificationForm.value = true
    addAssistantTurn(`Sure! Here's your current search context — feel free to change anything:\n📍 **${ctx.destination}** · 📅 ${_fmtDate(ctx.checkIn)} → ${_fmtDate(ctx.checkOut)} · 👥 ${ctx.adults} adult${ctx.adults > 1 ? 's' : ''}, ${ctx.rooms} room${ctx.rooms > 1 ? 's' : ''} 👇`)
    return
  }

  // ── Filter reset / clear commands ────────────────────────────────────────────
  // MUST run before the invalidBudget check — "Reset budget filter" / "Clear budget filter"
  // would otherwise be falsely flagged as an invalid budget by the budget regex.
  const resetClearVerb = /(?:reset|clear)\s+(?:the\s+)?/i.source
  const isResetAll    = new RegExp(`\\b(?:reset|clear)\\s+all\\s+(?:the\\s+)?(?:add.?on\\s+)?filters?\\b`, 'i').test(query)
  const isResetStar   = new RegExp(`\\b${resetClearVerb}(?:star(?:\\s+rating)?|rating)\\s*filter\\b`, 'i').test(query)
  const isResetHotel  = new RegExp(`\\b${resetClearVerb}(?:hotel(?:\\s+name)?|name)\\s*filter\\b`, 'i').test(query)
  const isResetBudget = new RegExp(`\\b${resetClearVerb}(?:budget|price|cost)\\s*filter\\b`, 'i').test(query)

  if (isResetAll || isResetStar || isResetHotel || isResetBudget) {
    const prev = { ...activeFilters.value }
    if (isResetAll) {
      clearFilters()
      addAssistantTurn('✅ All add-on filters cleared! Showing the full hotel feed.')
    } else if (isResetStar) {
      setFilters({ ...prev, starRating: null, starRatings: null })
      addAssistantTurn('✅ Star rating filter cleared! Showing hotels of all star ratings.')
    } else if (isResetHotel) {
      setFilters({ ...prev, hotelName: null })
      addAssistantTurn('✅ Hotel name filter cleared! Showing all hotels.')
    } else if (isResetBudget) {
      setFilters({ ...prev, budgetMin: null, budgetMax: null })
      addAssistantTurn('✅ Budget filter cleared! Showing hotels at all price points.')
    }
    return
  }

  // ── Extract everything from the query ──
  const extracted = extractAllFromQuery(query)

  // ── Check for invalid budget before anything else ──
  const budgetCheck = extractBudgetFromText(query)
  if (budgetCheck.invalidBudget) {
    addAssistantTurn("🚫 I'm afraid I can't apply that budget filter — it looks like a word rather than a number. Please specify a numeric budget, like **₹5000** or **max 5000**.")
    return
  }

  // ── Check if user is filtering the existing feed FIRST (before hotel-related check) ──
  if (isFilterOnExistingFeed(query, extracted)) {
    applyFilterFromChat(query, extracted)
    return
  }

  if (!isHotelRelated(query) && turns.value.length > 1) {
    leadData.value.query = query
    leadStep.value = 'offered'
    addAssistantTurn(
      "Hmm, that's outside my expertise. 🤔 I specialize in hotel discovery. Would you like me to connect you with our **sales team** who can assist? You can also reach us directly at **1800-2099-100**. (Yes / No)"
    )
    return
  }

  // ── Mandatory: destination ──
  if (!extracted.destination && !currentDestination.value) {
    clarificationAnswers.value = {
      ...(extracted.checkIn ? { check_in: extracted.checkIn } : {}),
      ...(extracted.checkOut ? { check_out: extracted.checkOut } : {}),
      ...(extracted.adults ? { adults: String(extracted.adults) } : {}),
      ...(extracted.rooms ? { rooms: String(extracted.rooms) } : {}),
    }
    // Pre-select add-on filters from query in the form
    if (extracted.starRatings?.length) setFiltersFromQuery({ starRatings: extracted.starRatings, starRating: extracted.starRatings[0] })
    else if (extracted.starRating) setFiltersFromQuery({ starRating: extracted.starRating })
    if (extracted.hotelName) setFiltersFromQuery({ hotelName: extracted.hotelName })
    if (extracted.budgetMax) setFiltersFromQuery({ budgetMax: extracted.budgetMax })
    if (extracted.budgetMin) setFiltersFromQuery({ budgetMin: extracted.budgetMin })
    clarificationMissingFields.value = ['destination', 'check_in', 'check_out']
    showClarificationForm.value = true
    addAssistantTurn("I'd love to help! 🏨 To find the perfect hotel, I just need a few quick details:")
    return
  }

  const dest = extracted.destination || currentDestination.value!

  // ── Dates missing → offer smart defaults ──
  if (!extracted.checkIn && !extracted.checkOut && !currentDestination.value) {
    const tomorrow = _getTomorrow(); const dayAfter = _getDayAfter(tomorrow)
    const adults = extracted.adults || 1; const rooms = extracted.rooms || 1
    pendingSmartFill.value = {
      destination: dest, checkIn: tomorrow, checkOut: dayAfter,
      adults, rooms, starRating: extracted.starRating, starRatings: extracted.starRatings,
      hotelName: extracted.hotelName, budgetMin: extracted.budgetMin, budgetMax: extracted.budgetMax,
    }
    promptStep.value = 'smart-fill-offered'
    addAssistantTurn(
      `Great choice — **${dest}**! 🌆\n\nI can search right away using smart defaults:\n📅 Check-in: **${_fmtDate(tomorrow)}** · Check-out: **${_fmtDate(dayAfter)}**\n👥 **${adults} adult${adults > 1 ? 's' : ''}** · ${rooms} room${rooms > 1 ? 's' : ''}\n\nReply **yes** to search now, or **no** to set custom dates.`
    )
    return
  }

  // ── DONNA transparency: reusing previous search context for new destination ──
  if (prevSearchContext.value && extracted.destination &&
      extracted.destination.toLowerCase() !== prevSearchContext.value.destination.toLowerCase() &&
      !extracted.checkIn && !extracted.checkOut) {
    const ctx = prevSearchContext.value
    const adults = extracted.adults || ctx.adults
    const rooms = extracted.rooms || ctx.rooms
    addAssistantTurn(
      `🗺️ Searching **${dest}** — since you haven't specified dates or guests, I'm reusing your previous details:\n📅 Check-in: **${_fmtDate(ctx.checkIn)}** · Check-out: **${_fmtDate(ctx.checkOut)}**\n👥 **${adults} adult${adults > 1 ? 's' : ''}** · ${rooms} room${rooms > 1 ? 's' : ''}\n\n_If you'd like to change anything, just say "change dates" or "change adults"._`
    )
  }

  // ── All required present — start new search ──
  currentDestination.value = dest
  fetchWeatherForPanel(dest)
  fetchWeatherPunchline(dest)

  // Clear old filters, then apply only what's in this query
  clearFilters()
  setFiltersFromQuery({
    starRating: extracted.starRating,
    starRatings: extracted.starRatings?.length ? extracted.starRatings : null,
    hotelName: extracted.hotelName,
    budgetMin: extracted.budgetMin,
    budgetMax: extracted.budgetMax,
  })

  // ── Store context for DONNA transparency on future queries ──
  const checkIn = extracted.checkIn || prevSearchContext.value?.checkIn || _getTomorrow()
  const checkOut = extracted.checkOut || prevSearchContext.value?.checkOut || _getDayAfter(checkIn)
  prevSearchContext.value = {
    destination: dest,
    checkIn,
    checkOut,
    adults: extracted.adults || prevSearchContext.value?.adults || 1,
    rooms: extracted.rooms || prevSearchContext.value?.rooms || 1,
  }

  addThinkingTurn('Donna is searching for you...')
  resetSessionId(); sessionId.value = useSessionId()
  showWeatherPanel.value = false; weatherPanelData.value = null
  nearbyCities.value = []; showNearbyCities.value = false
  curatedAlsoEmpty.value = false; isAutoScanningCurated.value = false
  startSearch(query, sessionId.value)
}

function handleHotelSelected(hotelId: string): void {
  navigateTo(`/hotels/${hotelId}`)
}

function handleRetry(): void {
  const lastUserTurn = [...turns.value].reverse().find((t) => t.role === 'user')
  if (lastUserTurn) handleSubmit(lastUserTurn.content)
}

function useSuggestion(text: string): void {
  handleSubmit(text)
}

// ─── Curated accept / reject ──────────────────────────────────────────────────
async function acceptCurated(): Promise<void> {
  addThinkingTurn('Loading curated hotel list...')
  await loadCuratedFeed()
  clearThinking()
  addAssistantTurn(`✨ Updated with ${hotels.value.length} curated hotel${hotels.value.length !== 1 ? 's' : ''}. These are hand-picked for you!`)
}

function rejectCurated(): void {
  dismissCurated()
  addAssistantTurn("No problem! The current results are still displayed on the right.")
}

// ─── Watchers ─────────────────────────────────────────────────────────────────
watch(thinkingMessage, (msg) => { if (msg) addThinkingTurn(msg) })
watch(pendingCurated, (val) => { if (val && curatedMessage.value) clearThinking() })

// ① Immediate zero-results detection — fires as soon as initial_hotels arrives empty
watch(earlyZeroResults, (val) => {
  if (!val) return
  // Use 'filters' reason when filters are pre-applied from the query
  startZeroResultsEarlyPhase(hasFilters.value ? 'filters' : 'no_raw')
})

watch(searchState, (state) => {
  if (state === 'complete') {
    clearThinking()
    if (!pendingCurated.value) {
      const count = hotels.value.length
      if (count > 0) {
        if (isAutoScanningCurated.value) {
          // Phase 1 already shown (filter zero case during has_results) — run phase 2
          finalizeCuratedLoad()
        } else if (hasFilters.value && filteredHotels.value.length === 0) {
          // All hotels filtered out, wasn't caught during has_results — run full flow
          triggerZeroResultsFlow('filters')
        } else {
          const shown = filteredHotels.value.length
          const total = count
          const filterNote = hasFilters.value && shown < total ? ` (${shown} match your filters)` : ''
          addAssistantTurn(
            `✅ Found ${total} hotel${total !== 1 ? 's' : ''}${filterNote} for you. Click any card to see full details.`
          )
        }
      } else if (earlyZeroResults.value) {
        // Phase 1 already showed the message — now run Phase 2 (curated load)
        finalizeCuratedLoad()
      } else {
        // Fallback: earlyZeroResults didn't fire (edge case) — run full flow
        startZeroResultsEarlyPhase(hasFilters.value ? 'filters' : 'no_raw')
        finalizeCuratedLoad()
      }
    }
  } else if (state === 'has_results' && hotels.value.length > 0) {
    clearThinking()
    if (hasFilters.value && filteredHotels.value.length === 0) {
      // Hotels arrived but all filtered out — show instant curated message
      addAssistantTurn(
        `Found ${hotels.value.length} hotel${hotels.value.length !== 1 ? 's' : ''} — but none match your filters. **Scanning our curated inventory for a better match...** 🔍`
      )
      startZeroResultsEarlyPhase('filters')
    } else {
      // Hotels arriving — keep weather card visible; user can scroll to see both
      addAssistantTurn(
        `Found ${hotels.value.length} hotel${hotels.value.length !== 1 ? 's' : ''} — enriching results in the background...`
      )
    }
  } else if (state === 'error' && searchError.value) {
    clearThinking()
    addAssistantTurn(`Sorry, I hit a snag: ${searchError.value.message}`)
  }
})

// Watch for client-side filters eliminating all results (reactive — fires when filteredHotels changes)
watch([() => filteredHotels.value.length, searchState], ([filtered, state]) => {
  if (filtered === 0 && hotels.value.length > 0 && hasFilters.value && !isAutoScanningCurated.value) {
    if (state === 'has_results') {
      // Immediate feedback — curated load happens when search completes
      startZeroResultsEarlyPhase('filters')
    } else if (state === 'complete') {
      triggerZeroResultsFlow('filters')
    }
  }
})
</script>

<template>
  <div class="page-root">
    <div class="bg-orb bg-orb-1" />
    <div class="bg-orb bg-orb-2" />

    <!-- Header -->
    <header class="app-header">
      <div class="header-inner">
        <div class="logo">
          <img src="/tc-logo.png" alt="Thomas Cook India" class="tc-logo-img" />
          <div>
            <span class="logo-name">NexTrip AI</span>
            <span class="logo-tag">powered by Thomas Cook India</span>
          </div>
        </div>
        <div class="header-badge">
          <span class="pulse-dot" />
          AI Powered
        </div>
        <button v-if="turns.length > 0" class="clear-chat-btn" title="Clear chat and start fresh" @click="handleClearChat">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none"><path d="M3 6h18M8 6V4h8v2M19 6l-1 14H6L5 6" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>
          Clear Chat
        </button>
      </div>
    </header>

    <!-- Main Content -->
    <main class="main-content">

      <!-- Donna welcome hero — always visible, compact when chat is active -->
      <div class="welcome-hero" :class="{ 'welcome-hero--compact': turns.length > 0 }">
        <div class="donna-avatar">
          <!-- Sleek Donna face SVG (looking right, Copilot-style) -->
          <svg viewBox="0 0 64 64" fill="none" xmlns="http://www.w3.org/2000/svg" width="48" height="48">
            <circle cx="32" cy="29" r="18" stroke="rgba(255,255,255,0.9)" stroke-width="1.8" fill="none"/>
            <circle cx="36.5" cy="26.5" r="4" fill="rgba(255,255,255,0.95)"/>
            <circle cx="38.2" cy="25.5" r="1.8" fill="#6366F1"/>
            <circle cx="39" cy="25" r="0.7" fill="white"/>
            <circle cx="27.5" cy="27.5" r="3" fill="rgba(255,255,255,0.85)"/>
            <circle cx="28.8" cy="26.8" r="1.3" fill="#6366F1"/>
            <path d="M25 35 Q32 41 39 35" stroke="rgba(255,255,255,0.9)" stroke-width="1.5" fill="none" stroke-linecap="round"/>
            <line x1="32" y1="11" x2="32" y2="7" stroke="rgba(255,255,255,0.75)" stroke-width="1.6" stroke-linecap="round"/>
            <circle cx="32" cy="6" r="2" fill="rgba(255,255,255,0.8)"/>
            <rect x="10" y="26" width="5" height="9" rx="2.5" fill="rgba(255,255,255,0.4)"/>
            <rect x="49" y="26" width="5" height="9" rx="2.5" fill="rgba(255,255,255,0.4)"/>
          </svg>
        </div>
        <div class="donna-intro">
          <h2 class="donna-name">Donna <span class="donna-sparkle">✨</span></h2>
          <span class="donna-acronym">Destination Oriented Neural Network Assistant</span>
          <p class="donna-tagline" v-show="turns.length === 0">
            <!-- Ghost element holds max-line height so container never jumps -->
            <span class="donna-tagline-ghost" aria-hidden="true">{{ donnaLongestLine }}</span>
            <span class="donna-tagline-text">{{ donnaText }}<span class="cursor" :class="{ blink: donnaCursor }">|</span></span>
          </p>
        </div>
        <div v-if="turns.length === 0" class="suggestions-grid">
          <button v-for="s in suggestions" :key="s" class="suggestion-chip" @click="useSuggestion(s)">
            {{ s }}
          </button>
        </div>
      </div>

      <!-- Collapse hint tooltip -->
      <Transition name="fade">
        <div v-if="showCollapseHint && showRightPanel" class="collapse-hint">
          💡 Tip: Use the <strong>‹ ›</strong> arrows to collapse/expand panels for more room.
          <button class="hint-close" @click="showCollapseHint = false">✕</button>
        </div>
      </Transition>

      <!-- Split layout -->
      <div class="content-layout" :class="{ 'with-results': hasResults || showRightPanel }">

        <!-- ── Chat Panel ──────────────────────────────────────────────── -->
        <div
          v-show="!chatCollapsed"
          class="chat-panel"
          :class="{ 'chat-compact': hasResults }"
        >
          <!-- Collapse button (only in split view) -->
          <button v-if="showRightPanel && !resultsCollapsed" class="panel-collapse-btn panel-collapse-left" title="Collapse chat" @click="collapseChat">
            ‹
          </button>

          <div v-if="turns.length > 0" class="chat-messages">
            <ChatWindow :turns="turns" />
          </div>

          <!-- Clarification form -->
          <div v-if="showClarificationForm" class="clarification-form">
            <p class="clarif-label">🔍 Please fill in the missing details:</p>
            <div class="clarif-field">
              <label>City / Destination</label>
              <input v-model="clarificationAnswers['destination']" type="text" placeholder="e.g. Goa, Dubai, Bangkok" />
            </div>
            <div class="clarif-field">
              <label>Check-in Date</label>
              <input v-model="clarificationAnswers['check_in']" type="date" :min="todayIso" />
            </div>
            <div class="clarif-field">
              <label>Check-out Date</label>
              <input
                v-model="clarificationAnswers['check_out']"
                type="date"
                :min="checkOutMinDate"
                :disabled="!clarificationAnswers['check_in']"
              />
              <span v-if="!clarificationAnswers['check_in']" class="clarif-hint">Select check-in date first</span>
            </div>
            <div class="clarif-row">
              <div class="clarif-field">
                <label>Adults</label>
                <input v-model="clarificationAnswers['adults']" type="number" min="1" max="10" placeholder="1" />
              </div>
              <div class="clarif-field">
                <label>Rooms</label>
                <input v-model="clarificationAnswers['rooms']" type="number" min="1" max="10" placeholder="1" />
              </div>
            </div>
            <!-- Show pre-applied filters if any -->
            <div v-if="hasFilters" class="clarif-filters-preview">
              <span class="clarif-filters-label">✨ Add-on filters detected:</span>
              <span v-if="activeFilters.hotelName" class="clarif-filter-tag">🏨 "{{ activeFilters.hotelName }}"</span>
              <span v-if="activeFilters.starRatings?.length" class="clarif-filter-tag">⭐ {{ activeFilters.starRatings.join('★ & ') }}★</span>
              <span v-else-if="activeFilters.starRating" class="clarif-filter-tag">⭐ {{ activeFilters.starRating }}★</span>
              <span v-if="activeFilters.budgetMax" class="clarif-filter-tag">💰 ≤ ₹{{ activeFilters.budgetMax.toLocaleString() }}</span>
            </div>
            <div class="clarif-actions">
              <button class="btn-primary" @click="submitClarification">Search Hotels</button>
              <button class="btn-ghost" @click="skipClarification">Skip / Auto-fill</button>
            </div>
          </div>

          <div class="chat-input-wrap">
            <div class="input-row">
              <ChatInput style="flex: 1; min-width: 0;" :disabled="isSearching" :history="userHistory" @submit="handleSubmit" />
              <button
                class="additional-info-btn"
                :class="{ 'filters-active': hasFilters }"
                title="Additional filters"
                @click="showAdditionalInfo = !showAdditionalInfo"
              >
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none">
                  <line x1="4" y1="6" x2="20" y2="6" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
                  <line x1="8" y1="12" x2="20" y2="12" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
                  <line x1="12" y1="18" x2="20" y2="18" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
                </svg>
                Filters
                <span v-if="hasFilters" class="filter-dot" />
              </button>
            </div>

            <!-- Additional Info panel -->
            <Transition name="slide-down">
              <div v-if="showAdditionalInfo" class="additional-info-panel">
                <p class="ai-panel-title">🎯 Refine your search</p>
                <div class="ai-fields">
                  <div class="ai-field">
                    <label>Hotel Name / Brand</label>
                    <input v-model="filterHotelName" type="text" placeholder="e.g. Taj, Marriott, Hilton" />
                  </div>
                  <div class="ai-field">
                    <label>Star Rating <span class="clarif-hint">(select multiple)</span></label>
                    <div class="star-buttons">
                      <button
                        v-for="s in [1,2,3,4,5]"
                        :key="s"
                        class="star-btn"
                        :class="{ active: filterStar.includes(s) }"
                        @click="filterStar.includes(s) ? filterStar.splice(filterStar.indexOf(s),1) : filterStar.push(s)"
                      >{{ s }}★</button>
                    </div>
                  </div>
                  <div class="ai-row">
                    <div class="ai-field">
                      <label>Min Budget (₹/night)</label>
                      <input v-model.number="filterBudgetMin" type="number" placeholder="e.g. 2000" />
                    </div>
                    <div class="ai-field">
                      <label>Max Budget (₹/night)</label>
                      <input v-model.number="filterBudgetMax" type="number" placeholder="e.g. 8000" />
                    </div>
                  </div>
                </div>
                <div class="ai-actions">
                  <button class="btn-primary" @click="applyAdditionalFilters">Apply Filters</button>
                  <button class="btn-ghost" @click="clearAdditionalFilters">Clear All</button>
                </div>
              </div>
            </Transition>
          </div>
        </div>

        <!-- Chat expand button (when collapsed) -->
        <button v-if="chatCollapsed && hasResults" class="panel-expand-btn panel-expand-chat" title="Expand chat" @click="expandChat">
          <span>💬</span>
          <span class="expand-label">Chat</span>
        </button>

        <!-- ── Results Panel ───────────────────────────────────────────── -->
        <div
          v-if="showRightPanel"
          v-show="!resultsCollapsed"
          ref="resultsPanelRef"
          class="results-panel"
        >
          <!-- Results expand button (collapse results) -->
          <button v-if="showRightPanel && !chatCollapsed" class="panel-collapse-btn panel-collapse-right" title="Collapse results" @click="collapseResults">
            ›
          </button>

          <div v-if="searchState === 'error' && searchError" class="results-section">
            <ErrorState :error="searchError" @retry="handleRetry" />
          </div>
          <div v-else class="results-section">

            <!-- ── Weather Card (always shown when data exists, above hotel results) ── -->
            <Transition name="weather-slide">
              <div v-if="weatherPanelData" class="weather-panel-wrap">
                <WeatherCard
                  :weather="weatherPanelData"
                  :city="currentDestination || weatherPanelData.city"
                />

                <!-- Nearby cities chips (shown after curated also fails) -->
                <Transition name="fade">
                  <div v-if="showNearbyCities && nearbyCities.length > 0" class="nearby-cities-wrap">
                    <p class="nearby-title">🗺️ Explore nearby cities</p>
                    <div class="nearby-chips">
                      <button
                        v-for="nc in nearbyCities"
                        :key="nc.name"
                        class="nearby-chip"
                        @click="useSuggestion(`Hotels in ${nc.name}`)"
                      >
                        <span class="nearby-chip-name">{{ nc.name }}</span>
                        <span class="nearby-chip-meta">{{ nc.country }} · {{ nc.distance_km }} km</span>
                      </button>
                    </div>
                  </div>
                </Transition>
              </div>
            </Transition>

            <!-- ── Normal hotel results ── -->
            <template v-if="hasResults">
              <div class="results-header">
                <div class="results-title-wrap">
                  <span class="results-title">{{ resultHeaderText }}</span>
                  <span v-if="hasFilters" class="filter-badge">
                    🎯 Filters active
                    <button class="filter-clear-x" @click="clearAdditionalFilters">✕</button>
                  </span>
                </div>
                <div class="results-header-right">
                  <span v-if="isPollingInBackground" class="live-badge">
                    <span class="pulse-dot" />
                    Enriching
                  </span>
                  <span v-else-if="searchState === 'complete'" class="complete-badge">
                    ✓ Complete
                  </span>
                </div>
              </div>

              <!-- Curated feed prompt -->
              <div v-if="pendingCurated" class="curated-prompt">
                <div class="curated-prompt-inner">
                  <span class="curated-icon">✨</span>
                  <div class="curated-body">
                    <p class="curated-msg">{{ curatedMessage }}</p>
                    <div class="curated-actions">
                      <button class="btn-yes" :disabled="loadingCurated" @click="acceptCurated">
                        <span v-if="loadingCurated">Loading...</span>
                        <span v-else>Yes, refresh results</span>
                      </button>
                      <button class="btn-no" :disabled="loadingCurated" @click="rejectCurated">No thanks</button>
                    </div>
                  </div>
                </div>
              </div>

              <!-- No filter results warning -->
              <div v-if="hasFilters && filteredHotels.length === 0 && hotels.length > 0" class="no-filter-results">
                <span>😕 No hotels match your current filters.</span>
                <button class="btn-ghost btn-sm" @click="clearAdditionalFilters">Clear filters</button>
              </div>

              <HotelList
                :hotels="filteredHotels"
                :search-state="searchState"
                @hotel-selected="handleHotelSelected"
              />
            </template>
          </div>
        </div>

        <!-- Results expand button (when collapsed) -->
        <button v-if="resultsCollapsed && showRightPanel" class="panel-expand-btn panel-expand-results" title="Expand results" @click="expandResults">
          <span>🏨</span>
          <span class="expand-label">Results ({{ filteredHotels.length }})</span>
        </button>

      </div>
    </main>
  </div>
</template>

<style scoped>
.page-root {
  min-height: 100vh;
  background: var(--app-bg);
  position: relative;
  overflow-x: hidden;
}

.bg-orb { position: fixed; border-radius: 50%; filter: blur(80px); pointer-events: none; z-index: 0; }
.bg-orb-1 { width: 600px; height: 600px; background: radial-gradient(circle, rgba(99,102,241,0.12) 0%, transparent 70%); top: -200px; right: -100px; }
.bg-orb-2 { width: 500px; height: 500px; background: radial-gradient(circle, rgba(139,92,246,0.10) 0%, transparent 70%); bottom: 0; left: -100px; }

/* Header */
.app-header { position: sticky; top: 0; z-index: 50; background: rgba(10,15,30,0.75); backdrop-filter: blur(20px); -webkit-backdrop-filter: blur(20px); border-bottom: 1px solid rgba(255,255,255,0.07); }
.header-inner { max-width: 1400px; margin: 0 auto; padding: 0 20px; height: 60px; display: flex; align-items: center; justify-content: space-between; }
.logo { display: flex; align-items: center; gap: 10px; }
.logo-name { display: block; font-size: 1rem; font-weight: 800; color: white; line-height: 1.1; font-family: 'Plus Jakarta Sans', 'Inter', sans-serif; }
.logo-tag { display: block; font-size: 0.65rem; color: rgba(148,163,184,0.8); line-height: 1; }
.tc-logo-img { height: 34px; width: auto; object-fit: contain; flex-shrink: 0; filter: brightness(1.05) drop-shadow(0 0 4px rgba(255,255,255,0.15)); }
.header-badge { display: flex; align-items: center; gap: 6px; font-size: 0.78rem; font-weight: 600; color: rgba(148,163,184,0.9); background: rgba(99,102,241,0.12); border: 1px solid rgba(99,102,241,0.2); padding: 5px 12px; border-radius: 20px; }
.pulse-dot { width: 7px; height: 7px; background: #4ADE80; border-radius: 50%; animation: pulse-dot 2s ease-in-out infinite; display: inline-block; }
@keyframes pulse-dot { 0%, 100% { opacity: 1; transform: scale(1); } 50% { opacity: 0.6; transform: scale(0.8); } }

/* Main */
.main-content { max-width: 1400px; margin: 0 auto; padding: 0 20px 60px; position: relative; z-index: 1; }

/* ── Donna Hero ── */
.welcome-hero { display: flex; flex-direction: column; align-items: center; text-align: center; padding: 60px 20px 36px; gap: 20px; }
.welcome-hero--compact { padding: 18px 20px 10px; gap: 6px; flex-direction: row; justify-content: flex-start; text-align: left; border-bottom: 1px solid rgba(255,255,255,0.07); margin-bottom: 10px; }
.welcome-hero--compact .donna-avatar { width: 40px; height: 40px; animation: none; box-shadow: none; flex-shrink: 0; }
.welcome-hero--compact .donna-avatar svg { width: 24px; height: 24px; }
.welcome-hero--compact .donna-name { font-size: 1.1rem; }
.welcome-hero--compact .donna-intro { flex-direction: row; align-items: center; gap: 10px; flex-wrap: wrap; }
.donna-avatar { width: 80px; height: 80px; background: linear-gradient(135deg, #6366F1 0%, #8B5CF6 60%, #A78BFA 100%); border-radius: 50%; display: flex; align-items: center; justify-content: center; animation: float 3.5s ease-in-out infinite; box-shadow: 0 0 40px rgba(99,102,241,0.4), 0 0 0 8px rgba(99,102,241,0.1); }
.donna-emoji { font-size: 2.2rem; }
@keyframes float { 0%, 100% { transform: translateY(0); } 50% { transform: translateY(-10px); } }
.donna-intro { display: flex; flex-direction: column; align-items: center; gap: 8px; }
.donna-name { font-size: 2.4rem; font-weight: 800; color: white; margin: 0; font-family: 'Plus Jakarta Sans', 'Inter', sans-serif; background: linear-gradient(135deg, #fff 0%, rgba(99,102,241,0.9) 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; }
.donna-sparkle { -webkit-text-fill-color: initial; }
.donna-acronym { font-size: 0.7rem; font-weight: 500; letter-spacing: 0.04em; color: rgba(139,92,246,0.85); text-transform: uppercase; margin-top: 2px; }
/* Tagline: ghost element holds the height of the longest line */
.donna-tagline { font-size: 1.05rem; color: rgba(148,163,184,0.9); max-width: 540px; margin: 0; line-height: 1.6; position: relative; }
.donna-tagline-ghost { visibility: hidden; display: block; pointer-events: none; user-select: none; }
.donna-tagline-text { position: absolute; top: 0; left: 0; right: 0; }
.cursor { display: inline-block; color: #6366F1; font-weight: 300; }
.cursor.blink { animation: blink 1s step-end infinite; }
@keyframes blink { 0%, 100% { opacity: 1; } 50% { opacity: 0; } }

.suggestions-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; width: 100%; max-width: 640px; margin-top: 4px; }
.suggestion-chip { background: rgba(255,255,255,0.06); border: 1px solid rgba(255,255,255,0.1); color: rgba(226,232,240,0.85); font-size: 0.82rem; padding: 10px 14px; border-radius: 12px; cursor: pointer; transition: background 0.2s, border-color 0.2s, transform 0.15s; font-family: 'Inter', sans-serif; text-align: left; line-height: 1.4; }
.suggestion-chip:hover { background: rgba(99,102,241,0.18); border-color: rgba(99,102,241,0.4); transform: translateY(-2px); }

/* ── Collapse Hint ── */
.collapse-hint {
  display: flex; align-items: center; gap: 10px; justify-content: center;
  background: rgba(99,102,241,0.12); border: 1px solid rgba(99,102,241,0.25);
  border-radius: 10px; padding: 8px 16px; margin: 12px 0 4px;
  font-size: 0.82rem; color: rgba(226,232,240,0.85);
}
.hint-close { background: none; border: none; color: rgba(148,163,184,0.7); cursor: pointer; font-size: 0.8rem; padding: 0 4px; margin-left: auto; }
.fade-enter-active, .fade-leave-active { transition: opacity 0.4s; }
.fade-enter-from, .fade-leave-to { opacity: 0; }

/* ── Layout ── */
.content-layout { display: flex; flex-direction: column; gap: 20px; margin-top: 12px; }
.content-layout.with-results { flex-direction: row; align-items: flex-start; gap: 12px; }

/* ── Panel collapse/expand buttons ── */
.panel-collapse-btn {
  position: absolute; top: 50%; transform: translateY(-50%);
  width: 20px; height: 48px;
  background: rgba(99,102,241,0.18); border: 1px solid rgba(99,102,241,0.3);
  color: rgba(148,163,184,0.9); border-radius: 4px;
  cursor: pointer; font-size: 1rem; line-height: 1;
  display: flex; align-items: center; justify-content: center;
  transition: background 0.2s, color 0.2s; z-index: 10;
}
.panel-collapse-btn:hover { background: rgba(99,102,241,0.35); color: white; }
.panel-collapse-left { right: -10px; }
.panel-collapse-right { left: -10px; }

.panel-expand-btn {
  display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 4px;
  width: 44px; padding: 14px 0;
  background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1);
  border-radius: 12px; cursor: pointer; color: rgba(148,163,184,0.8);
  transition: background 0.2s; flex-shrink: 0; writing-mode: initial;
}
.panel-expand-btn:hover { background: rgba(99,102,241,0.18); color: white; }
.expand-label { font-size: 0.6rem; writing-mode: vertical-rl; transform: rotate(180deg); font-family: 'Inter', sans-serif; white-space: nowrap; }

/* ── Chat Panel ── */
.chat-panel {
  background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.08);
  border-radius: 20px; backdrop-filter: blur(12px); overflow: hidden;
  transition: all 0.4s cubic-bezier(0.16, 1, 0.3, 1); min-height: 80px;
  flex: 1 1 auto; position: relative;
}
.content-layout.with-results .chat-panel {
  flex: 0 0 38%; min-width: 280px; max-width: 400px;
  position: sticky; top: 76px;
  max-height: calc(100vh - 100px); overflow-y: auto;
}
.chat-messages { min-height: 60px; max-height: 360px; overflow-y: auto; display: flex; flex-direction: column; }
.content-layout.with-results .chat-messages { max-height: calc(100vh - 280px); }
.chat-input-wrap { padding: 10px 14px 14px; border-top: 1px solid rgba(255,255,255,0.06); }
.input-row { display: flex; align-items: flex-end; gap: 8px; }

/* Clarification form */
.clarification-form { padding: 14px 16px; border-top: 1px solid rgba(255,255,255,0.06); display: flex; flex-direction: column; gap: 10px; }
.clarif-label { font-size: 0.85rem; font-weight: 600; color: rgba(226,232,240,0.9); margin: 0; }
.clarif-field { display: flex; flex-direction: column; gap: 4px; }
.clarif-field label { font-size: 0.75rem; color: rgba(148,163,184,0.8); font-weight: 500; }
.clarif-field input { background: rgba(255,255,255,0.06); border: 1px solid rgba(255,255,255,0.12); border-radius: 8px; color: white; font-size: 0.85rem; padding: 8px 12px; outline: none; transition: border-color 0.2s; font-family: 'Inter', sans-serif; }
.clarif-field input:focus { border-color: rgba(99,102,241,0.5); }
.clarif-row { display: flex; gap: 10px; }
.clarif-row .clarif-field { flex: 1; }
.clarif-actions { display: flex; gap: 8px; margin-top: 4px; }
.clarif-filters-preview { display: flex; flex-wrap: wrap; gap: 6px; align-items: center; padding: 6px 10px; background: rgba(99,102,241,0.08); border: 1px solid rgba(99,102,241,0.2); border-radius: 8px; }
.clarif-filters-label { font-size: 0.72rem; color: rgba(139,92,246,0.9); font-weight: 600; }
.clarif-filter-tag { font-size: 0.72rem; color: rgba(226,232,240,0.85); background: rgba(99,102,241,0.15); border: 1px solid rgba(99,102,241,0.25); padding: 2px 8px; border-radius: 12px; }

/* Additional Info btn */
.additional-info-btn { display: flex; align-items: center; gap: 5px; background: rgba(255,255,255,0.06); border: 1px solid rgba(255,255,255,0.1); color: rgba(148,163,184,0.85); font-size: 0.75rem; font-weight: 600; padding: 8px 10px; border-radius: 10px; cursor: pointer; transition: background 0.2s; white-space: nowrap; font-family: 'Inter', sans-serif; flex-shrink: 0; position: relative; }
.additional-info-btn:hover { background: rgba(99,102,241,0.15); border-color: rgba(99,102,241,0.3); color: rgba(226,232,240,0.9); }
.additional-info-btn.filters-active { background: rgba(99,102,241,0.2); border-color: rgba(99,102,241,0.5); color: #818CF8; }
.filter-dot { width: 6px; height: 6px; background: #818CF8; border-radius: 50%; position: absolute; top: 4px; right: 4px; }

/* Additional Info Panel */
.additional-info-panel { background: rgba(15,20,40,0.95); border: 1px solid rgba(99,102,241,0.25); border-radius: 14px; padding: 16px; margin-top: 10px; backdrop-filter: blur(16px); }
.ai-panel-title { font-size: 0.88rem; font-weight: 700; color: rgba(226,232,240,0.9); margin: 0 0 12px; }
.ai-fields { display: flex; flex-direction: column; gap: 12px; }
.ai-field { display: flex; flex-direction: column; gap: 4px; }
.ai-field label { font-size: 0.75rem; color: rgba(148,163,184,0.8); font-weight: 500; }
.ai-field input { background: rgba(255,255,255,0.06); border: 1px solid rgba(255,255,255,0.1); border-radius: 8px; color: white; font-size: 0.85rem; padding: 8px 12px; outline: none; transition: border-color 0.2s; font-family: 'Inter', sans-serif; }
.ai-field input:focus { border-color: rgba(99,102,241,0.5); }
.ai-row { display: flex; gap: 10px; }
.ai-row .ai-field { flex: 1; }
.star-buttons { display: flex; gap: 6px; }
.star-btn { background: rgba(255,255,255,0.06); border: 1px solid rgba(255,255,255,0.1); color: rgba(148,163,184,0.8); font-size: 0.82rem; padding: 6px 14px; border-radius: 8px; cursor: pointer; transition: all 0.2s; font-family: 'Inter', sans-serif; }
.star-btn.active { background: rgba(99,102,241,0.25); border-color: rgba(99,102,241,0.5); color: #818CF8; font-weight: 700; }
.star-btn:hover { background: rgba(99,102,241,0.15); border-color: rgba(99,102,241,0.3); }
.ai-actions { display: flex; gap: 8px; margin-top: 14px; }
.slide-down-enter-active, .slide-down-leave-active { transition: all 0.28s cubic-bezier(0.16, 1, 0.3, 1); }
.slide-down-enter-from, .slide-down-leave-to { opacity: 0; transform: translateY(-10px); }

/* ── Results Panel ── */
.results-panel {
  flex: 1 1 auto; min-width: 0;
  overflow-y: auto;
  max-height: calc(100vh - 100px);
  position: relative;
}
@keyframes slideUp { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }
.results-section {}
.results-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 16px; flex-wrap: wrap; gap: 8px; }
.results-title-wrap { display: flex; align-items: center; gap: 10px; flex-wrap: wrap; }
.results-title { font-size: 1rem; font-weight: 700; color: white; font-family: 'Plus Jakarta Sans', 'Inter', sans-serif; }
.filter-badge { display: flex; align-items: center; gap: 6px; font-size: 0.75rem; font-weight: 600; color: #818CF8; background: rgba(99,102,241,0.15); border: 1px solid rgba(99,102,241,0.3); padding: 3px 8px; border-radius: 20px; }
.filter-clear-x { background: none; border: none; color: #818CF8; cursor: pointer; font-size: 0.75rem; padding: 0; line-height: 1; }
.results-header-right { display: flex; align-items: center; gap: 8px; }
.live-badge { display: flex; align-items: center; gap: 6px; font-size: 0.75rem; font-weight: 600; color: #4ADE80; background: rgba(74,222,128,0.1); border: 1px solid rgba(74,222,128,0.25); padding: 4px 10px; border-radius: 20px; }
.complete-badge { font-size: 0.75rem; font-weight: 600; color: #34D399; background: rgba(52,211,153,0.1); border: 1px solid rgba(52,211,153,0.2); padding: 4px 10px; border-radius: 20px; }

.no-filter-results { display: flex; align-items: center; gap: 12px; background: rgba(251,191,36,0.08); border: 1px solid rgba(251,191,36,0.2); border-radius: 10px; padding: 10px 14px; font-size: 0.85rem; color: rgba(251,191,36,0.9); margin-bottom: 14px; }

/* Curated prompt */
.curated-prompt { margin-bottom: 16px; }
.curated-prompt-inner { display: flex; align-items: flex-start; gap: 12px; background: linear-gradient(135deg, rgba(99,102,241,0.12), rgba(139,92,246,0.10)); border: 1px solid rgba(99,102,241,0.3); border-radius: 14px; padding: 14px 16px; backdrop-filter: blur(8px); }
.curated-icon { font-size: 1.4rem; flex-shrink: 0; margin-top: 1px; }
.curated-body { flex: 1; }
.curated-msg { flex: 1; font-size: 0.88rem; color: rgba(226,232,240,0.9); margin: 0 0 10px; line-height: 1.5; }
.curated-actions { display: flex; gap: 8px; flex-wrap: wrap; }

/* Buttons */
.btn-primary { background: linear-gradient(135deg, #6366F1, #8B5CF6); color: white; border: none; border-radius: 8px; padding: 8px 18px; font-size: 0.84rem; font-weight: 600; cursor: pointer; transition: opacity 0.2s, transform 0.15s; font-family: 'Inter', sans-serif; }
.btn-primary:hover { opacity: 0.88; transform: translateY(-1px); }
.btn-ghost { background: rgba(255,255,255,0.07); color: rgba(148,163,184,0.9); border: 1px solid rgba(255,255,255,0.1); border-radius: 8px; padding: 8px 18px; font-size: 0.84rem; font-weight: 500; cursor: pointer; transition: background 0.2s; font-family: 'Inter', sans-serif; }
.btn-ghost:hover { background: rgba(255,255,255,0.12); }
.btn-sm { padding: 5px 12px; font-size: 0.78rem; }
.btn-yes { background: linear-gradient(135deg, #6366F1, #8B5CF6); color: white; border: none; border-radius: 8px; padding: 7px 16px; font-size: 0.82rem; font-weight: 600; cursor: pointer; transition: opacity 0.2s, transform 0.15s; font-family: 'Inter', sans-serif; }
.btn-yes:hover:not(:disabled) { opacity: 0.88; transform: translateY(-1px); }
.btn-yes:disabled { opacity: 0.5; cursor: not-allowed; }
.btn-no { background: rgba(255,255,255,0.07); color: rgba(148,163,184,0.9); border: 1px solid rgba(255,255,255,0.1); border-radius: 8px; padding: 7px 16px; font-size: 0.82rem; font-weight: 500; cursor: pointer; transition: background 0.2s; font-family: 'Inter', sans-serif; }
.btn-no:hover:not(:disabled) { background: rgba(255,255,255,0.12); }
.btn-no:disabled { opacity: 0.5; cursor: not-allowed; }

/* ── Weather panel ── */
.weather-panel-wrap { margin-bottom: 20px; display: flex; flex-direction: column; gap: 16px; }
.weather-slide-enter-active { transition: all 0.5s cubic-bezier(0.16, 1, 0.3, 1); }
.weather-slide-leave-active { transition: all 0.3s ease; }
.weather-slide-enter-from { opacity: 0; transform: translateY(16px) scale(0.97); }
.weather-slide-leave-to { opacity: 0; transform: scale(0.96); }

/* ── Nearby cities ── */
.nearby-cities-wrap { background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.08); border-radius: 16px; padding: 16px; }
.nearby-title { font-size: 0.85rem; font-weight: 700; color: rgba(226,232,240,0.9); margin: 0 0 12px; }
.nearby-chips { display: flex; flex-direction: column; gap: 8px; }
.nearby-chip {
  display: flex; align-items: center; justify-content: space-between;
  background: rgba(99,102,241,0.08); border: 1px solid rgba(99,102,241,0.2);
  border-radius: 10px; padding: 10px 14px; cursor: pointer;
  transition: background 0.2s, border-color 0.2s, transform 0.15s;
  text-align: left;
}
.nearby-chip:hover { background: rgba(99,102,241,0.18); border-color: rgba(99,102,241,0.4); transform: translateX(4px); }
.nearby-chip-name { font-size: 0.88rem; font-weight: 700; color: white; }
.nearby-chip-meta { font-size: 0.74rem; color: rgba(148,163,184,0.7); }

/* Responsive */
@media (max-width: 768px) {
  .content-layout.with-results { flex-direction: column; }
  .content-layout.with-results .chat-panel { flex: none; width: 100%; max-width: none; position: static; border-right: none; border-bottom: 1px solid rgba(99,102,241,0.18); }
  .donna-name { font-size: 1.8rem; }
  .welcome-hero { padding: 40px 16px 28px; }
  .panel-collapse-btn, .panel-expand-btn { display: none; }
  .app-header .header-inner { padding: 0 12px; }
  .header-badge { display: none; }
  .results-panel { padding: 12px 8px; }
  .chat-input-area { padding: 10px 10px 14px; }
  .welcome-search { padding: 0 12px; }
  .clarification-form { padding: 14px; margin: 0 8px; }
}

/* ── Clear Chat button ── */
.clear-chat-btn {
  display: flex; align-items: center; gap: 6px;
  background: rgba(239,68,68,0.1); border: 1px solid rgba(239,68,68,0.25);
  color: rgba(252,165,165,0.85); font-size: 0.75rem; font-weight: 600;
  padding: 5px 12px; border-radius: 20px; cursor: pointer;
  transition: background 0.2s, border-color 0.2s, color 0.2s;
  font-family: 'Inter', sans-serif;
}
.clear-chat-btn:hover { background: rgba(239,68,68,0.2); border-color: rgba(239,68,68,0.5); color: #fca5a5; }

/* ── Checkout date hint ── */
.clarif-hint { font-size: 0.72rem; color: rgba(251,191,36,0.75); margin-top: 2px; }
.clarif-field input:disabled { opacity: 0.45; cursor: not-allowed; }

/* ── Panel divider (sleek vertical line between panels) ── */
.content-layout.with-results .chat-panel {
  border-right: 1px solid rgba(99,102,241,0.18);
}
</style>

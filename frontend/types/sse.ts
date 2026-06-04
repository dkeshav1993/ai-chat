import type { HotelSearchResult } from './search'

export type SearchState = 'idle' | 'searching' | 'has_results' | 'polling' | 'complete' | 'error'

export type SseErrorCode =
  | 'NO_AUTOSUGGEST_RESULT'
  | 'VALIDATION_ERROR'
  | 'NO_RESULT'
  | 'DOWNSTREAM_NULL'
  | 'DOWNSTREAM_ERROR'
  | 'DOWNSTREAM_TIMEOUT'
  | 'POLL_TIMEOUT'
  | 'TOKEN_REFRESH_FAILED'
  | 'INTERNAL_ERROR'

export interface SseInitialHotelsEvent {
  hotels: HotelSearchResult[]
  count: number
}

export interface SseHotelsBatchEvent {
  hotels: HotelSearchResult[]
  batchIndex: number
}

export interface SseThinkingEvent {
  message: string
}

export interface SseSearchCompleteEvent {
  totalHotels: number
  searchKey: string
  autoSuggestId: string
}

export interface SseCuratedReadyEvent {
  message: string
  searchKey: string
  sessionId: string
}

export interface SseErrorEvent {
  code: SseErrorCode
  message: string
  recoverable: boolean
  capability?: string
}

export interface SseClarificationNeededEvent {
  message: string
  missing_fields: string[]
  hotel_name_filter?: string | null
}

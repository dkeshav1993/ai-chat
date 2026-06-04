export interface AutoSuggestEntry {
  uniqueId: string
  type: string
  name: string
  cityName?: string
  stateName?: string
  countryName?: string
}

export interface HotelProviderInfo {
  providerName?: string
  providerHotelID?: string
  totalFare?: number
  currency?: string
  [key: string]: unknown
}

export interface HotelAddress {
  addressLine1?: string
  addressLine2?: string
  city?: string
  state?: string
  country?: string
  zipCode?: string
  [key: string]: unknown
}

export interface HotelContact {
  phone?: string
  email?: string
  address?: HotelAddress
  [key: string]: unknown
}

export interface HotelSearchResult {
  vervotechHotelId: string
  name: string
  starRating?: string
  currency?: string
  heroImage?: string
  contact?: HotelContact
  providerInfo?: HotelProviderInfo[]
  [key: string]: unknown
}

// Backward-compatible alias
export type HotelCard = HotelSearchResult

export interface SearchHistoryEntry {
  sessionId: string
  destination: string
  checkIn: string
  checkOut: string
  adultCount: number
  roomCount: number
}

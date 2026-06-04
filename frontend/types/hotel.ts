export interface HotelFacility {
  id?: string
  name?: string
  masterFacilityId?: string
  [key: string]: unknown
}

export interface HotelPolicy {
  title?: string
  text?: string
  [key: string]: unknown
}

export interface HotelCheckin {
  time?: string
  instructions?: string
  [key: string]: unknown
}

export interface HotelCheckout {
  time?: string
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

export interface HotelData {
  vervotechHotelId?: string
  name?: string
  description?: string
  starRating?: string
  currency?: string
  heroImage?: string
  contact?: HotelContact
  facilities?: HotelFacility[]
  policies?: HotelPolicy[]
  checkin?: HotelCheckin
  checkout?: HotelCheckout
  images?: unknown[]
  [key: string]: unknown
}

export interface HotelDetailsResponse {
  success: boolean
  status: number
  message: string
  searchKey: string
  autoSuggestId: string
  hotelData: HotelData
}

export interface RoomTotalPrice {
  source?: string
  parsedValue?: number
  [key: string]: unknown
}

export interface RoomRate {
  roomId?: string
  inputIndex?: number
  rateId?: string
  totalPrice?: RoomTotalPrice
  basePrice?: number
  taxes?: number
  boardBasis?: string
  refundability?: string
  cancelPenalties?: unknown[]
  amenities?: unknown[]
  [key: string]: unknown
}

export interface RoomImages {
  isDummy?: boolean
  data?: unknown[]
  [key: string]: unknown
}

export interface RoomOption {
  description?: string
  standardName?: string
  masterTitle?: string
  category?: string
  view?: string
  roomLocation?: string
  occupancyType?: string
  roomRates?: RoomRate[]
  images?: RoomImages
  [key: string]: unknown
}

export interface RoomData {
  hotelId: string
  standardRooms: RoomOption[]
}

import { ref } from 'vue'
import type { HotelData } from '~/types/hotel'

type DetailState = 'idle' | 'loading' | 'loaded' | 'error'

interface DetailError {
  code: string
  message: string
  recoverable: boolean
}

export function useHotelDetails() {
  const hotelData = ref<HotelData | null>(null)
  const detailState = ref<DetailState>('idle')
  const detailError = ref<DetailError | null>(null)

  async function fetchHotelDetails(hotelId: string, sessionId: string): Promise<void> {
    detailState.value = 'loading'
    detailError.value = null
    hotelData.value = null

    try {
      const params = new URLSearchParams({ session_id: sessionId })
      const response = await fetch(`/api/hotels/${encodeURIComponent(hotelId)}?${params}`)
      const body = await response.json()

      if (!response.ok) {
        const err = body?.detail ?? body
        detailError.value = {
          code: err?.code ?? 'DOWNSTREAM_ERROR',
          message: err?.message ?? 'Failed to load hotel details.',
          recoverable: err?.recoverable ?? true,
        }
        detailState.value = 'error'
        return
      }

      hotelData.value = body.data?.hotelData ?? null
      detailState.value = hotelData.value ? 'loaded' : 'error'
      if (!hotelData.value) {
        detailError.value = {
          code: 'NO_RESULT',
          message: 'No hotel data was returned.',
          recoverable: true,
        }
      }
    } catch (err) {
      detailError.value = {
        code: 'INTERNAL_ERROR',
        message: 'Could not load hotel details. Please try again.',
        recoverable: true,
      }
      detailState.value = 'error'
    }
  }

  return {
    hotelData,
    detailState,
    detailError,
    fetchHotelDetails,
  }
}

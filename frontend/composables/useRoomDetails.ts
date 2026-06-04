import { ref } from 'vue'
import type { RoomOption } from '~/types/room'

type RoomState = 'idle' | 'loading' | 'loaded' | 'error'

interface RoomError {
  code: string
  message: string
  recoverable: boolean
}

export function useRoomDetails() {
  const rooms = ref<RoomOption[]>([])
  const roomState = ref<RoomState>('idle')
  const roomError = ref<RoomError | null>(null)
  const pgRedirectUrl = ref<string>('')

  async function fetchRoomDetails(hotelId: string, sessionId: string): Promise<void> {
    roomState.value = 'loading'
    roomError.value = null
    rooms.value = []
    pgRedirectUrl.value = ''

    try {
      const params = new URLSearchParams({ session_id: sessionId })
      const response = await fetch(`/api/hotels/${encodeURIComponent(hotelId)}/rooms?${params}`)
      const body = await response.json()

      if (!response.ok) {
        const err = body?.detail ?? body
        roomError.value = {
          code: err?.code ?? 'DOWNSTREAM_ERROR',
          message: err?.message ?? 'Failed to load room details.',
          recoverable: err?.recoverable ?? true,
        }
        roomState.value = 'error'
        return
      }

      const roomData = body.data?.roomData
      rooms.value = Array.isArray(roomData?.standardRooms) ? roomData.standardRooms : []
      pgRedirectUrl.value = body.data?.pgRedirectUrl ?? ''
      roomState.value = 'loaded'
    } catch {
      roomError.value = {
        code: 'INTERNAL_ERROR',
        message: 'Could not load room details. Please try again.',
        recoverable: true,
      }
      roomState.value = 'error'
    }
  }

  return {
    rooms,
    roomState,
    roomError,
    pgRedirectUrl,
    fetchRoomDetails,
  }
}

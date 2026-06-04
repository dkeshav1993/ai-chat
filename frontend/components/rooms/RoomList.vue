<script setup lang="ts">
import type { RoomOption } from '~/types/room'
import type { SseErrorEvent } from '~/types/sse'

interface Props {
  rooms: RoomOption[]
  roomState: 'idle' | 'loading' | 'loaded' | 'error'
  pgRedirectUrl: string
  roomError?: { code: string; message: string; recoverable: boolean } | null
  hotelId?: string
}

const props = defineProps<Props>()
const emit = defineEmits<{
  retry: []
}>()

function handleRoomSelect(idx: number): void {
  if (props.hotelId) {
    navigateTo(`/hotels/${props.hotelId}/book/${idx}`)
  } else if (props.pgRedirectUrl) {
    // fallback for backward compat
    window.open(props.pgRedirectUrl, '_blank', 'noopener,noreferrer')
  }
}

const errorAsSseEvent = computed<SseErrorEvent | null>(() => {
  if (!props.roomError) return null
  return {
    code: props.roomError.code as SseErrorEvent['code'],
    message: props.roomError.message,
    recoverable: props.roomError.recoverable,
  }
})
</script>

<template>
  <div>
    <LoadingState v-if="props.roomState === 'loading'" message="Loading available rooms..." />

    <ErrorState
      v-else-if="props.roomState === 'error' && errorAsSseEvent"
      :error="errorAsSseEvent"
      @retry="emit('retry')"
    />

    <EmptyState
      v-else-if="props.roomState === 'loaded' && props.rooms.length === 0"
      title="No rooms available"
      message="There are no available rooms for this hotel at the moment. Please try different dates."
      icon="🛏️"
    />

    <div
      v-else-if="props.rooms.length > 0"
      class="grid gap-5 sm:grid-cols-2 lg:grid-cols-3"
    >
      <RoomCard
        v-for="(room, index) in props.rooms"
        :key="index"
        :room="room"
        :index="index"
        :style="{ animationDelay: `${index * 80}ms` }"
        @select="handleRoomSelect"
      />
    </div>
  </div>
</template>

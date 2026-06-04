<script setup lang="ts">
import type { HotelCard as HotelCardType } from '~/types/search'
import type { SearchState } from '~/types/sse'

import HotelCard from '~/components/hotels/HotelCard.vue'
import HotelCardSkeleton from '~/components/hotels/HotelCardSkeleton.vue'
import EmptyState from '~/components/shared/EmptyState.vue'

interface Props {
  hotels: HotelCardType[]
  searchState: SearchState
}

const props = defineProps<Props>()
const emit = defineEmits<{
  'hotel-selected': [hotelId: string]
}>()

const SKELETON_COUNT = 6

function onHotelSelect(hotelId: string): void {
  emit('hotel-selected', hotelId)
}
</script>

<template>
  <div>
    <!-- Searching: full skeleton grid -->
    <div
      v-if="props.searchState === 'searching'"
      class="grid gap-4 grid-cols-1 sm:grid-cols-2"
    >
      <HotelCardSkeleton v-for="n in SKELETON_COUNT" :key="n" />
    </div>

    <!-- Streaming / complete: show actual cards -->
    <div
      v-else-if="props.hotels.length > 0"
      class="grid gap-4 grid-cols-1 sm:grid-cols-2"
    >
      <HotelCard
        v-for="(hotel, i) in props.hotels"
        :key="hotel.hotelId"
        :hotel="hotel"
        :index="i"
        class="animate-slide-up"
        :style="{ animationDelay: `${Math.min(i * 60, 300)}ms` }"
        @select="onHotelSelect"
      />

      <!-- Trailing skeletons while still streaming -->
      <template v-if="props.searchState === 'streaming'">
        <HotelCardSkeleton v-for="n in 3" :key="`sk-${n}`" />
      </template>
    </div>

    <!-- No results after complete -->
    <EmptyState
      v-else-if="props.searchState === 'complete'"
      title="No hotels found"
      message="We couldn't find any hotels for your search. Try a different destination or date range."
      icon="🏨"
    />
  </div>
</template>

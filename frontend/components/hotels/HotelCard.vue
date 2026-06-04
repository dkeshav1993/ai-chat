<script setup lang="ts">
import type { HotelCard } from '~/types/search'
import { getHotelImageUrl, onImageError, extractFirstImageUrl } from '~/utils/hotelImages'

interface Props {
  hotel: HotelCard
  index?: number
}

const props = defineProps<Props>()
const emit = defineEmits<{
  select: [hotelId: string]
}>()

const city = computed(() => props.hotel.contact?.address?.city ?? '')

// Image priority: heroImage (API) → images array first link (API) → Unsplash mock
const imgUrl = computed(() => {
  const hero = props.hotel.heroImage
  if (hero && hero.trim()) return hero.trim()
  const fromArray = extractFirstImageUrl(props.hotel.images)
  if (fromArray) return fromArray
  return getHotelImageUrl(props.hotel.vervotechHotelId || city.value || 'hotel', props.index ?? 0)
})
const fallbackUrl = computed(() =>
  getHotelImageUrl(props.hotel.vervotechHotelId || city.value || 'hotel', props.index ?? 0)
)

function onSelect(): void {
  emit('select', props.hotel.vervotechHotelId)
}

const starRating = computed(() => parseFloat(String(props.hotel.starRating ?? '0')) || 0)
const price = computed(() => {
  const pi = props.hotel.providerInfo
  return Array.isArray(pi) && pi.length > 0 ? (pi[0].totalFare ?? 0) : 0
})
const currency = computed(() => props.hotel.currency ?? 'INR')

const starsArray = computed(() => {
  const full = Math.floor(starRating.value)
  const hasHalf = starRating.value % 1 >= 0.5
  const empty = 5 - full - (hasHalf ? 1 : 0)
  return [
    ...Array(full).fill('full'),
    ...(hasHalf ? ['half'] : []),
    ...Array(empty).fill('empty'),
  ]
})
</script>

<template>
  <div class="hotel-card" @click="onSelect">
    <!-- Image -->
    <div class="card-image-wrap">
      <img
        :src="imgUrl"
        :alt="hotel.name"
        class="card-image"
        loading="lazy"
        @error="(e) => onImageError(e, fallbackUrl)"
      />
      <div class="card-image-overlay" />

      <!-- Price badge on image -->
      <div v-if="price > 0" class="price-badge">
        <span class="price-currency">{{ currency }}</span>
        <span class="price-amount">{{ price.toLocaleString() }}</span>
        <span class="price-unit">/night</span>
      </div>
    </div>

    <!-- Content -->
    <div class="card-body">
      <h3 class="card-name">{{ hotel.name }}</h3>

      <div class="card-meta">
        <span v-if="city" class="card-city">
          <svg width="12" height="12" viewBox="0 0 24 24" fill="currentColor"><path d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7zm0 9.5c-1.38 0-2.5-1.12-2.5-2.5s1.12-2.5 2.5-2.5 2.5 1.12 2.5 2.5-1.12 2.5-2.5 2.5z"/></svg>
          {{ city }}
        </span>

        <span class="card-rating">
          <span
            v-for="(star, i) in starsArray"
            :key="i"
            class="star"
            :class="star === 'empty' ? 'star-empty' : 'star-filled'"
          >★</span>
          <span class="rating-value">{{ starRating.toFixed(1) }}</span>
        </span>
      </div>

      <button class="card-cta" @click.stop="onSelect">
        View Details
        <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="9 18 15 12 9 6"/></svg>
      </button>
    </div>
  </div>
</template>

<style scoped>
.hotel-card {
  background: #fff;
  border-radius: 16px;
  overflow: hidden;
  cursor: pointer;
  transition: transform 0.2s cubic-bezier(0.16,1,0.3,1), box-shadow 0.2s;
  box-shadow: 0 2px 8px rgba(0,0,0,0.12), 0 1px 2px rgba(0,0,0,0.08);
  display: flex;
  flex-direction: column;
}
.hotel-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 32px rgba(0,0,0,0.20), 0 4px 8px rgba(0,0,0,0.10);
}

.card-image-wrap {
  position: relative;
  height: 180px;
  overflow: hidden;
  flex-shrink: 0;
}
.card-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.4s ease;
}
.hotel-card:hover .card-image {
  transform: scale(1.04);
}
.card-image-overlay {
  position: absolute;
  inset: 0;
  background: linear-gradient(180deg, transparent 40%, rgba(0,0,0,0.45) 100%);
}

.rooms-badge {
  position: absolute;
  top: 10px;
  right: 10px;
  background: rgba(16, 185, 129, 0.9);
  color: white;
  font-size: 0.7rem;
  font-weight: 700;
  padding: 3px 9px;
  border-radius: 20px;
  backdrop-filter: blur(4px);
  letter-spacing: 0.02em;
}

.price-badge {
  position: absolute;
  bottom: 10px;
  left: 10px;
  display: flex;
  align-items: baseline;
  gap: 2px;
}
.price-currency {
  font-size: 0.7rem;
  font-weight: 600;
  color: rgba(255,255,255,0.85);
}
.price-amount {
  font-size: 1.1rem;
  font-weight: 800;
  color: #fff;
  font-family: 'Plus Jakarta Sans', 'Inter', sans-serif;
}
.price-unit {
  font-size: 0.7rem;
  color: rgba(255,255,255,0.75);
}

.card-body {
  padding: 14px 16px 16px;
  display: flex;
  flex-direction: column;
  gap: 8px;
  flex: 1;
}
.card-name {
  font-size: 0.9rem;
  font-weight: 700;
  color: #1E293B;
  line-height: 1.35;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  font-family: 'Plus Jakarta Sans', 'Inter', sans-serif;
}

.card-meta {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
}
.card-city {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 0.78rem;
  color: #64748B;
}
.card-rating {
  display: flex;
  align-items: center;
  gap: 2px;
}
.star {
  font-size: 0.8rem;
}
.star-filled { color: #F59E0B; }
.star-empty { color: #D1D5DB; }
.rating-value {
  font-size: 0.75rem;
  font-weight: 600;
  color: #64748B;
  margin-left: 2px;
}

.card-cta {
  margin-top: auto;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 4px;
  width: 100%;
  background: linear-gradient(135deg, #6366F1, #8B5CF6);
  color: white;
  font-size: 0.8rem;
  font-weight: 600;
  padding: 9px 16px;
  border-radius: 10px;
  border: none;
  cursor: pointer;
  transition: opacity 0.2s, transform 0.15s;
}
.card-cta:hover {
  opacity: 0.92;
  transform: translateY(-1px);
}
</style>

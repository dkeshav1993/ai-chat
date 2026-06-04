<script setup lang="ts">
import type { RoomOption } from '~/types/room'

interface Props {
  room: RoomOption
  index?: number
}

const props = defineProps<Props>()
const emit = defineEmits<{
  select: [index: number]
}>()

// Image carousel
const currentImageIndex = ref(0)

const FALLBACK_URLS = [
  'https://images.unsplash.com/photo-1631049307264-da0ec9d70304?w=800',
  'https://images.unsplash.com/photo-1618773928121-c32242e63f39?w=800',
  'https://images.unsplash.com/photo-1615874959474-d609969a20ed?w=800',
  'https://images.unsplash.com/photo-1566073771259-6a8506099945?w=800',
]

// Extract all image URLs from images.data[].links[0].providerHref or href
const imageList = computed<{ url: string; caption: string }[]>(() => {
  const imgs = (props.room.images?.data ?? []) as Record<string, unknown>[]
  const result: { url: string; caption: string }[] = []
  for (const img of imgs) {
    const links = (img.links ?? []) as Record<string, string>[]
    const href = links[0]?.providerHref || links[0]?.href || ''
    if (href) result.push({ url: href, caption: String(img.caption ?? '') })
  }
  return result
})

const displayImages = computed(() => {
  const list = imageList.value.length > 0
    ? imageList.value
    : [{ url: FALLBACK_URLS[(props.index ?? 0) % FALLBACK_URLS.length], caption: 'Room' }]
  return list.slice(0, 5)  // max 5 images
})

const currentImage = computed(() => displayImages.value[currentImageIndex.value])
const hasMultipleImages = computed(() => displayImages.value.length > 1)

function prevImage() {
  currentImageIndex.value =
    (currentImageIndex.value - 1 + displayImages.value.length) % displayImages.value.length
}
function nextImage() {
  currentImageIndex.value = (currentImageIndex.value + 1) % displayImages.value.length
}
function goToImage(i: number) {
  currentImageIndex.value = i
}
function handleImgError(e: Event) {
  const t = e.target as HTMLImageElement
  t.src = FALLBACK_URLS[(props.index ?? 0) % FALLBACK_URLS.length]
}

// Pricing
const firstRate = computed(() => props.room.roomRates?.[0])
const price = computed(() => {
  const p = firstRate.value?.totalPrice?.parsedValue
  return typeof p === 'number' && p > 0 ? p : (firstRate.value?.basePrice ?? 0)
})
const basePrice = computed(() => firstRate.value?.basePrice ?? 0)
const taxes = computed(() => firstRate.value?.taxes ?? 0)
const isRefundable = computed(() => firstRate.value?.refundability === 'Refundable')

// Amenities
const amenities = computed<string[]>(() => {
  const seen = new Set<string>()
  for (const rate of props.room.roomRates ?? []) {
    for (const a of (rate.amenities ?? []) as Record<string, string>[]) {
      if (a.name) seen.add(String(a.name))
    }
  }
  return [...seen]
})

// Meal plan
const mealPlanLabels: Record<string, string> = {
  BB: 'Bed & Breakfast',
  HB: 'Half Board',
  FB: 'Full Board',
  AI: 'All Inclusive',
  RO: 'Room Only',
}
const mealLabel = computed(() => {
  const b = firstRate.value?.boardBasis
  return b ? (mealPlanLabels[String(b)] ?? String(b)) : null
})

// Room type badge
const roomTypeColors: Record<string, string> = {
  STANDARD: 'badge-blue',
  SUPERIOR: 'badge-purple',
  SUITE: 'badge-gold',
  DELUXE: 'badge-teal',
}
const badgeClass = computed(
  () => roomTypeColors[String(props.room.category ?? '').toUpperCase()] ?? 'badge-blue'
)

// Amenity emoji icons
const AMENITY_ICONS: Record<string, string> = {
  'air conditioning': '\u2744\uFE0F',
  'parking': '\uD83D\uDE97',
  'gym': '\uD83C\uDFCB\uFE0F',
  'spa': '\uD83D\uDEBF',
  'pool': '\uD83C\uDFCA',
  'breakfast': '\u2615',
  'free wifi': '\uD83D\uDCF6',
  'wifi': '\uD83D\uDCF6',
  'safe': '\uD83D\uDD12',
  'tv': '\uD83D\uDCFA',
  'club lounge': '\u2728',
  'jacuzzi': '\uD83D\uDEBB',
  'room service': '\uD83D\uDCCB',
  'balcony': '\uD83C\uDFD9\uFE0F',
  'minibar': '\uD83C\uDF7E',
}
function amenityIcon(name: string): string {
  const lower = name.toLowerCase()
  for (const [key, icon] of Object.entries(AMENITY_ICONS)) {
    if (lower.includes(key)) return icon
  }
  return '\u2B50'
}
</script>

<template>
  <div class="room-card animate-slide-up">
    <!-- Image carousel -->
    <div class="room-image-wrap">
      <img
        :src="currentImage.url"
        :alt="currentImage.caption || String(room.standardName ?? 'Room')"
        class="room-image"
        loading="lazy"
        @error="handleImgError"
      />
      <div class="room-image-overlay" />

      <!-- Prev / Next  only when multiple images -->arrows 
      <template v-if="hasMultipleImages">
        <button class="carousel-btn carousel-prev" aria-label="Previous image" @click.stop="prevImage">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2.5" stroke-linecap="round"><polyline points="15 18 9 12 15 6"/></svg>
        </button>
        <button class="carousel-btn carousel-next" aria-label="Next image" @click.stop="nextImage">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2.5" stroke-linecap="round"><polyline points="9 18 15 12 9 6"/></svg>
        </button>
        <div class="carousel-dots">
          <button
            v-for="(_, i) in displayImages"
            :key="i"
            class="carousel-dot"
            :class="{ active: i === currentImageIndex }"
            :aria-label="`Image ${i + 1}`"
            @click.stop="goToImage(i)"
          />
        </div>
        <span class="image-count">{{ currentImageIndex + 1 }} / {{ displayImages.length }}</span>
      </template>

      <!-- Category badge -->
      <span v-if="room.category" class="room-type-badge" :class="badgeClass">
        {{ room.category }}
      </span>
    </div>

    <!-- Room content -->
    <div class="room-body">
      <div class="room-header">
        <h3 class="room-name">{{ room.standardName ?? 'Room' }}</h3>
        <span v-if="isRefundable" class="refund-badge">Refundable</span>
        <span v-else class="no-refund-badge">Non-refundable</span>
      </div>

      <p v-if="room.description" class="room-desc">{{ room.description }}</p>

      <!-- Features row -->
      <div class="room-features">
        <span v-if="room.occupancyType" class="room-feature">
          <svg width="13" height="13" viewBox="0 0 24 24" fill="currentColor"><path d="M16 11c1.66 0 2.99-1.34 2.99-3S17.66 5 16 5c-1.66 0-3 1.34-3 3s1.34 3 3 3zm-8 0c1.66 0 2.99-1.34 2.99-3S9.66 5 8 5C6.34 5 5 6.34 5 8s1.34 3 3 3zm0 2c-2.33 0-7 1.17-7 3.5V19h14v-2.5c0-2.33-4.67-3.5-7-3.5zm8 0c-.29 0-.62.02-.97.05 1.16.84 1.97 1.97 1.97 3.45V19h6v-2.5c0-2.33-4.67-3.5-7-3.5z"/></svg>
          {{ room.occupancyType }}
        </span>
        <span v-if="mealLabel" class="room-feature meal-feature">
          <svg width="13" height="13" viewBox="0 0 24 24" fill="currentColor"><path d="M18 3v2h-2V3H8v2H6V3H4v18h2v-2h2v2h8v-2h2v2h2V3h-2zM8 17H6v-2h2v2zm0-4H6v-2h2v2zm0-4H6V7h2v2zm10 8h-2v-2h2v2zm0-4h-2v-2h2v2zm0-4h-2V7h2v2z"/></svg>
          {{ mealLabel }}
        </span>
      </div>

      <!-- Amenities -->
      <div v-if="amenities.length > 0" class="amenities-section">
        <div class="amenities-label">Amenities</div>
        <div class="amenities-list">
          <span v-for="amenity in amenities" :key="amenity" class="amenity-chip">
            <span class="amenity-icon">{{ amenityIcon(amenity) }}</span>
            {{ amenity }}
          </span>
        </div>
      </div>

      <!-- Pricing breakdown -->
      <div v-if="price > 0" class="price-section">
        <div class="price-main">
          <span class="price-currency">&#8377;</span>
          <span class="price-value">{{ Number(price).toLocaleString('en-IN') }}</span>
          <span class="price-per">/night</span>
        </div>
        <div v-if="basePrice > 0 && taxes > 0" class="price-breakdown">
          <span>Base: {{ Number(basePrice).toLocaleString('en-IN', { maximumFractionDigits: 0 }) }}</span>
          <span class="breakdown-sep">+</span>
          <span>Taxes: {{ Number(taxes).toLocaleString('en-IN', { maximumFractionDigits: 0 }) }}</span>
        </div>
      </div>

      <!-- Book button -->
      <button class="book-btn" @click="emit('select', props.index ?? 0)">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="4" width="18" height="18" rx="2" ry="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg>
        Book This Room
      </button>
    </div>
  </div>
</template>

<style scoped>
.room-card {
  background: white;
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0,0,0,0.10);
  transition: transform 0.2s cubic-bezier(0.16,1,0.3,1), box-shadow 0.2s;
  display: flex;
  flex-direction: column;
}
.room-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 10px 28px rgba(0,0,0,0.15);
}

/* Image carousel */
.room-image-wrap {
  position: relative;
  height: 200px;
  overflow: hidden;
  flex-shrink: 0;
  background: #0f172a;
}
.room-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.4s ease;
}
.room-card:hover .room-image {
  transform: scale(1.04);
}
.room-image-overlay {
  position: absolute;
  inset: 0;
  background: linear-gradient(180deg, transparent 40%, rgba(0,0,0,0.55) 100%);
  pointer-events: none;
}
.carousel-btn {
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  width: 30px;
  height: 30px;
  border-radius: 50%;
  background: rgba(0,0,0,0.45);
  border: 1px solid rgba(255,255,255,0.2);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: background 0.2s, opacity 0.2s;
  opacity: 0;
  z-index: 5;
}
.room-image-wrap:hover .carousel-btn { opacity: 1; }
.carousel-prev { left: 8px; }
.carousel-next { right: 8px; }
.carousel-btn:hover { background: rgba(0,0,0,0.7); }

.carousel-dots {
  position: absolute;
  bottom: 32px;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  gap: 5px;
  z-index: 5;
}
.carousel-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: rgba(255,255,255,0.4);
  border: none;
  cursor: pointer;
  padding: 0;
  transition: background 0.2s, transform 0.2s;
}
.carousel-dot.active { background: white; transform: scale(1.3); }

.image-count {
  position: absolute;
  top: 8px;
  right: 8px;
  font-size: 0.68rem;
  font-weight: 600;
  color: white;
  background: rgba(0,0,0,0.5);
  padding: 2px 7px;
  border-radius: 20px;
  z-index: 5;
  backdrop-filter: blur(4px);
}
.room-type-badge {
  position: absolute;
  top: 10px;
  left: 10px;
  font-size: 0.68rem;
  font-weight: 700;
  padding: 3px 10px;
  border-radius: 20px;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  z-index: 5;
}
.badge-blue   { background: rgba(99,102,241,0.85);  color: white; }
.badge-purple { background: rgba(139,92,246,0.85);  color: white; }
.badge-gold   { background: rgba(245,158,11,0.9);   color: white; }
.badge-teal   { background: rgba(20,184,166,0.85);  color: white; }

/* Body */
.room-body {
  padding: 14px 16px 16px;
  display: flex;
  flex-direction: column;
  gap: 10px;
  flex: 1;
}
.room-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 8px;
}
.room-name {
  font-size: 0.95rem;
  font-weight: 700;
  color: #1E293B;
  line-height: 1.3;
  font-family: 'Plus Jakarta Sans', 'Inter', sans-serif;
  flex: 1;
}
.refund-badge {
  font-size: 0.7rem; font-weight: 600;
  color: #059669; background: #D1FAE5;
  padding: 3px 8px; border-radius: 20px; flex-shrink: 0;
}
.no-refund-badge {
  font-size: 0.7rem; font-weight: 600;
  color: #B45309; background: #FEF3C7;
  padding: 3px 8px; border-radius: 20px; flex-shrink: 0;
}
.room-desc {
  font-size: 0.82rem; color: #64748B; line-height: 1.5; margin: 0;
  display: -webkit-box; -webkit-line-clamp: 2;
  -webkit-box-orient: vertical; overflow: hidden;
}
.room-features { display: flex; flex-wrap: wrap; gap: 6px; }
.room-feature {
  display: inline-flex; align-items: center; gap: 4px;
  font-size: 0.78rem; color: #475569;
  background: #F1F5F9; border-radius: 6px; padding: 4px 8px;
}
.meal-feature { color: #7C3AED; background: #EDE9FE; }

/* Amenities */
.amenities-section { display: flex; flex-direction: column; gap: 6px; }
.amenities-label {
  font-size: 0.72rem; font-weight: 700;
  text-transform: uppercase; letter-spacing: 0.07em; color: #94A3B8;
}
.amenities-list { display: flex; flex-wrap: wrap; gap: 5px; }
.amenity-chip {
  display: inline-flex; align-items: center; gap: 4px;
  font-size: 0.76rem; font-weight: 500;
  color: #1E40AF; background: #EFF6FF;
  border: 1px solid #BFDBFE;
  border-radius: 6px; padding: 3px 8px;
}
.amenity-icon { font-size: 0.82rem; line-height: 1; }

/* Pricing */
.price-section {
  background: linear-gradient(135deg, #FFF7ED, #FFFBEB);
  border: 1px solid #FDE68A;
  border-radius: 10px; padding: 10px 12px;
  display: flex; flex-direction: column; gap: 4px;
}
.price-main { display: flex; align-items: baseline; gap: 2px; }
.price-currency { font-size: 0.9rem; font-weight: 700; color: #92400E; }
.price-value {
  font-size: 1.4rem; font-weight: 800; color: #78350F;
  font-family: 'Plus Jakarta Sans', 'Inter', sans-serif; line-height: 1;
}
.price-per { font-size: 0.75rem; color: #92400E; margin-left: 2px; }
.price-breakdown {
  display: flex; align-items: center; gap: 6px;
  font-size: 0.72rem; color: #B45309;
}
.breakdown-sep { color: #D97706; font-weight: 700; }

/* Book button */
.book-btn {
  margin-top: auto;
  display: flex; align-items: center; justify-content: center; gap: 8px;
  background: linear-gradient(135deg, #F59E0B, #D97706);
  color: white; font-size: 0.85rem; font-weight: 700;
  padding: 11px; border-radius: 10px; border: none; cursor: pointer;
  transition: opacity 0.2s, transform 0.15s;
  font-family: 'Plus Jakarta Sans', 'Inter', sans-serif;
  box-shadow: 0 4px 12px rgba(245,158,11,0.3);
}
.book-btn:hover { opacity: 0.92; transform: translateY(-1px); }

@keyframes slide-up {
  from { opacity: 0; transform: translateY(20px); }
  to   { opacity: 1; transform: translateY(0); }
}
.animate-slide-up { animation: slide-up 0.4s ease forwards; }
</style>

<script setup lang="ts">
import type { HotelData } from '~/types/hotel'
import { getHotelImageUrl, onImageError, extractFirstImageUrl } from '~/utils/hotelImages'

interface Props {
  hotelData: HotelData
  hotelId?: string
}

const props = defineProps<Props>()
const emit = defineEmits<{
  'view-rooms': []
}>()

const hotel = computed(() => props.hotelData)
const name = computed(() => (hotel.value.name ?? 'Hotel Details') as string)

const rating = computed(() => parseFloat(String(hotel.value.starRating ?? hotel.value.rating ?? '0')) || 0)
const starsArray = computed(() => {
  const full = Math.floor(rating.value)
  const hasHalf = rating.value % 1 >= 0.5
  const empty = 5 - full - (hasHalf ? 1 : 0)
  return [
    ...Array(full).fill('full'),
    ...(hasHalf ? ['half'] : []),
    ...Array(empty).fill('empty'),
  ]
})

const amenityIcons: Record<string, string> = {
  'wifi': '📶', 'free wifi': '📶',
  'pool': '🏊', 'swimming pool': '🏊',
  'spa': '💆', 'gym': '🏋️', 'fitness': '🏋️',
  'restaurant': '🍽️', 'bar': '🍸', 'parking': '🅿️',
  'concierge': '🛎️', 'room service': '🛎️',
  'beach': '🏖️', 'butler': '🤵',
  'tennis': '🎾', 'golf': '⛳',
  'business': '💼', 'conference': '🏢',
  'breakfast': '🥐', 'airport': '✈️',
}

function getAmenityIcon(amenity: string): string {
  const key = amenity.toLowerCase()
  for (const [k, icon] of Object.entries(amenityIcons)) {
    if (key.includes(k)) return icon
  }
  return '✓'
}

const amenities = computed((): string[] => {
  const f = hotel.value.facilities
  if (!Array.isArray(f)) return []
  return f.map(item => (typeof item === 'string' ? item : ((item as Record<string, unknown>).name as string ?? ''))).filter(Boolean)
})

const policies = computed(() => {
  const p = hotel.value.policies
  if (!Array.isArray(p)) return []
  return p
    .filter(item => item && (item.text || item.title))
    .map(item => ({
      label: item.title ?? '',
      value: item.text ?? '',
    }))
})

const city = computed(() => hotel.value.contact?.address?.city ?? '')
const country = computed(() => hotel.value.contact?.address?.country ?? '')
const address = computed(() => {
  const a = hotel.value.contact?.address
  if (!a) return ''
  return [a.addressLine1, a.addressLine2, a.city, a.state, a.country]
    .filter(Boolean).join(', ')
})
const checkInTime = computed(() => hotel.value.checkin?.time ?? '')
const checkOutTime = computed(() => hotel.value.checkout?.time ?? '')

const heroImgUrl = computed(() => {
  // Priority 1: heroImage field from API
  const apiHero = hotel.value.heroImage
  if (apiHero && apiHero.trim()) return apiHero.trim()
  // Priority 2: first real image from images (handles both array and {isDummy, data} shapes)
  const fromImages = extractFirstImageUrl(hotel.value.images)
  if (fromImages) return fromImages
  // Final fallback: Unsplash mock — only when no real image available
  return getHotelImageUrl(String(props.hotelId ?? hotel.value.vervotechHotelId ?? hotel.value.name ?? ''))
})
const fallbackImgUrl = computed(() =>
  getHotelImageUrl(String(city.value || 'hotel'), 5)
)

// ─── XXL Image Gallery ────────────────────────────────────────────────────────
interface GalleryImage { url: string; caption: string; category: string }

const allXxlImages = computed<GalleryImage[]>(() => {
  const imagesField = hotel.value.images
  if (!imagesField) return []
  let dataArr: unknown[] = []
  if (Array.isArray(imagesField)) {
    dataArr = imagesField
  } else if (typeof imagesField === 'object' && imagesField !== null) {
    const block = imagesField as Record<string, unknown>
    dataArr = Array.isArray(block.data) ? block.data : []
  }
  const result: GalleryImage[] = []
  for (const item of dataArr) {
    const img = item as Record<string, unknown>
    const links = Array.isArray(img.links) ? (img.links as Record<string, string>[]) : []
    const xxlLink = links.find(l => l.size === 'XXL')
    const url = xxlLink?.providerHref || xxlLink?.href || ''
    if (url) {
      result.push({
        url,
        caption: String(img.caption ?? ''),
        category: String(img.category ?? ''),
      })
    }
  }
  return result
})

const hasGallery = computed(() => allXxlImages.value.length > 0)
const previewImages = computed(() => allXxlImages.value.slice(0, 5))
const remainingCount = computed(() => Math.max(0, allXxlImages.value.length - 5))

// Lightbox / popup state
const lightboxOpen = ref(false)
const lightboxIndex = ref(0)

function openLightbox(index: number) {
  lightboxIndex.value = index
  lightboxOpen.value = true
}
function closeLightbox() {
  lightboxOpen.value = false
}
function prevLightbox() {
  lightboxIndex.value = (lightboxIndex.value - 1 + allXxlImages.value.length) % allXxlImages.value.length
}
function nextLightbox() {
  lightboxIndex.value = (lightboxIndex.value + 1) % allXxlImages.value.length
}
function handleKeydown(e: KeyboardEvent) {
  if (!lightboxOpen.value) return
  if (e.key === 'Escape') closeLightbox()
  else if (e.key === 'ArrowLeft') prevLightbox()
  else if (e.key === 'ArrowRight') nextLightbox()
}

onMounted(() => window.addEventListener('keydown', handleKeydown))
onUnmounted(() => window.removeEventListener('keydown', handleKeydown))
</script>

<template>
  <div class="hotel-detail animate-fade-in">
    <!-- Hero Image -->
    <div class="hero-wrap">
      <img
        :src="heroImgUrl"
        :alt="name"
        class="hero-img"
        loading="eager"
        @error="(e) => onImageError(e, fallbackImgUrl)"
      />
      <div class="hero-overlay" />
      <div class="hero-content">
        <div class="hero-stars">
          <span
            v-for="(s, i) in starsArray"
            :key="i"
            :class="s === 'empty' ? 'star-empty' : 'star-filled'"
          >★</span>
          <span class="rating-num">{{ rating.toFixed(1) }}</span>
        </div>
        <h1 class="hero-title">{{ name }}</h1>
        <div class="hero-meta">
          <span v-if="city" class="hero-chip">
            <svg width="12" height="12" viewBox="0 0 24 24" fill="currentColor"><path d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7z"/></svg>
            {{ city }}{{ country ? ', ' + country : '' }}
          </span>
          <span v-if="checkInTime" class="hero-chip">↓ In {{ checkInTime }}</span>
          <span v-if="checkOutTime" class="hero-chip">↑ Out {{ checkOutTime }}</span>
        </div>
      </div>
    </div>

    <!-- Body -->
    <div class="detail-body">

      <!-- Description -->
      <section v-if="hotel.description" class="detail-section">
        <h2 class="section-title">About This Hotel</h2>
        <p class="section-text">{{ hotel.description }}</p>
      </section>

      <!-- Photo Gallery (only if XXL images available) -->
      <section v-if="hasGallery" class="detail-section">
        <div class="gallery-header">
          <h2 class="section-title">Photo Gallery</h2>
          <button
            v-if="allXxlImages.length > 5"
            class="view-all-btn"
            @click="openLightbox(0)"
          >
            View all {{ allXxlImages.length }} photos
          </button>
        </div>
        <div class="gallery-grid">
          <div
            v-for="(img, i) in previewImages"
            :key="i"
            class="gallery-thumb-wrap"
            :class="{ 'gallery-thumb-last': i === 4 && remainingCount > 0 }"
            @click="openLightbox(i)"
          >
            <img
              :src="img.url"
              :alt="img.caption || img.category || 'Hotel photo'"
              class="gallery-thumb"
              loading="lazy"
            />
            <div class="gallery-thumb-overlay">
              <span class="gallery-thumb-icon">🔍</span>
            </div>
            <!-- +N overlay on last thumbnail -->
            <div v-if="i === 4 && remainingCount > 0" class="gallery-more-overlay">
              <span class="gallery-more-text">+{{ remainingCount }}</span>
              <span class="gallery-more-sub">more photos</span>
            </div>
          </div>
        </div>
      </section>

      <!-- Address -->
      <section v-if="address" class="detail-section">
        <h2 class="section-title">Location</h2>
        <div class="address-row">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#6366F1" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/><circle cx="12" cy="10" r="3"/>
          </svg>
          <span class="address-text">{{ address }}</span>
        </div>
      </section>

      <!-- Amenities -->
      <section v-if="amenities.length > 0" class="detail-section">
        <h2 class="section-title">Amenities</h2>
        <div class="amenities-grid">
          <div v-for="amenity in amenities" :key="amenity" class="amenity-chip">
            <span class="amenity-icon">{{ getAmenityIcon(amenity) }}</span>
            <span>{{ amenity }}</span>
          </div>
        </div>
      </section>

      <!-- Policies -->
      <section v-if="policies.length > 0" class="detail-section">
        <h2 class="section-title">Hotel Policies</h2>
        <div class="policies-list">
          <div v-for="policy in policies" :key="policy.label" class="policy-row">
            <span class="policy-label">{{ policy.label }}</span>
            <span class="policy-value">{{ policy.value }}</span>
          </div>
        </div>
      </section>

      <!-- CTA -->
      <div class="cta-wrap">
        <button class="cta-btn" @click="emit('view-rooms')">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/></svg>
          View Available Rooms
        </button>
      </div>
    </div>

    <!-- ── Lightbox Modal ── -->
    <Teleport to="body">
      <Transition name="lightbox">
        <div v-if="lightboxOpen" class="lightbox-overlay" @click.self="closeLightbox">
          <div class="lightbox-box">
            <!-- Close -->
            <button class="lightbox-close" aria-label="Close" @click="closeLightbox">✕</button>

            <!-- Counter -->
            <div class="lightbox-counter">
              {{ lightboxIndex + 1 }} / {{ allXxlImages.length }}
            </div>

            <!-- Image -->
            <div class="lightbox-img-wrap">
              <img
                :src="allXxlImages[lightboxIndex].url"
                :alt="allXxlImages[lightboxIndex].caption"
                class="lightbox-img"
              />
            </div>

            <!-- Caption -->
            <div v-if="allXxlImages[lightboxIndex].caption" class="lightbox-caption">
              <span v-if="allXxlImages[lightboxIndex].category" class="lightbox-cat-badge">
                {{ allXxlImages[lightboxIndex].category }}
              </span>
              {{ allXxlImages[lightboxIndex].caption }}
            </div>

            <!-- Nav arrows -->
            <button
              v-if="allXxlImages.length > 1"
              class="lightbox-nav lightbox-prev"
              aria-label="Previous"
              @click="prevLightbox"
            >
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2.5" stroke-linecap="round"><polyline points="15 18 9 12 15 6"/></svg>
            </button>
            <button
              v-if="allXxlImages.length > 1"
              class="lightbox-nav lightbox-next"
              aria-label="Next"
              @click="nextLightbox"
            >
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2.5" stroke-linecap="round"><polyline points="9 18 15 12 9 6"/></svg>
            </button>

            <!-- Dot strip -->
            <div class="lightbox-dots">
              <button
                v-for="(_, i) in allXxlImages"
                :key="i"
                class="lightbox-dot"
                :class="{ active: i === lightboxIndex }"
                :aria-label="`Photo ${i + 1}`"
                @click="lightboxIndex = i"
              />
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>
  </div>
</template>

<style scoped>
.hotel-detail {
  background: white;
  border-radius: 20px;
  overflow: hidden;
  box-shadow: 0 4px 24px rgba(0,0,0,0.15);
}

/* ── Hero ── */
.hero-wrap { position: relative; height: 320px; overflow: hidden; }
@media (max-width: 640px) { .hero-wrap { height: 220px; } }
.hero-img { width: 100%; height: 100%; object-fit: cover; }
.hero-overlay {
  position: absolute; inset: 0;
  background: linear-gradient(180deg, rgba(0,0,0,0.1) 0%, rgba(0,0,0,0.75) 100%);
}
.hero-content { position: absolute; bottom: 0; left: 0; right: 0; padding: 24px; }
.hero-stars { display: flex; align-items: center; gap: 2px; margin-bottom: 6px; }
.star-filled { color: #FCD34D; font-size: 1rem; }
.star-empty { color: rgba(255,255,255,0.4); font-size: 1rem; }
.rating-num { font-size: 0.8rem; font-weight: 700; color: rgba(255,255,255,0.9); margin-left: 6px; }
.hero-title {
  font-size: 1.75rem; font-weight: 800; color: white; line-height: 1.2;
  margin: 0 0 10px; font-family: 'Plus Jakarta Sans', 'Inter', sans-serif;
}
@media (max-width: 640px) { .hero-title { font-size: 1.25rem; } }
.hero-meta { display: flex; flex-wrap: wrap; gap: 8px; }
.hero-chip {
  display: inline-flex; align-items: center; gap: 4px;
  background: rgba(255,255,255,0.18); backdrop-filter: blur(4px);
  color: white; font-size: 0.78rem; font-weight: 500;
  padding: 4px 10px; border-radius: 20px; border: 1px solid rgba(255,255,255,0.25);
}

/* ── Body ── */
.detail-body { padding: 28px; display: flex; flex-direction: column; gap: 28px; }
@media (max-width: 640px) { .detail-body { padding: 20px 16px; } }
.detail-section {}
.section-title {
  font-size: 1rem; font-weight: 700; color: #1E293B;
  margin: 0 0 12px; font-family: 'Plus Jakarta Sans', 'Inter', sans-serif;
}
.section-text { font-size: 0.9rem; color: #475569; line-height: 1.7; margin: 0; }

/* ── Gallery ── */
.gallery-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 12px; }
.gallery-header .section-title { margin-bottom: 0; }
.view-all-btn {
  font-size: 0.8rem; font-weight: 600;
  color: #6366F1; background: #EEF2FF;
  border: 1px solid #C7D2FE; border-radius: 20px;
  padding: 5px 14px; cursor: pointer; transition: background 0.2s;
}
.view-all-btn:hover { background: #E0E7FF; }

.gallery-grid {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 6px;
}
@media (max-width: 640px) {
  .gallery-grid { grid-template-columns: repeat(3, 1fr); }
}
.gallery-thumb-wrap {
  position: relative;
  aspect-ratio: 4/3;
  border-radius: 8px;
  overflow: hidden;
  cursor: pointer;
  background: #E2E8F0;
}
.gallery-thumb {
  width: 100%; height: 100%; object-fit: cover;
  transition: transform 0.3s ease;
}
.gallery-thumb-wrap:hover .gallery-thumb { transform: scale(1.06); }
.gallery-thumb-overlay {
  position: absolute; inset: 0;
  background: rgba(0,0,0,0); display: flex;
  align-items: center; justify-content: center;
  transition: background 0.2s;
  font-size: 1.2rem;
  opacity: 0;
}
.gallery-thumb-wrap:hover .gallery-thumb-overlay { background: rgba(0,0,0,0.35); opacity: 1; }
.gallery-more-overlay {
  position: absolute; inset: 0;
  background: rgba(0,0,0,0.6);
  display: flex; flex-direction: column;
  align-items: center; justify-content: center;
  color: white;
}
.gallery-more-text { font-size: 1.4rem; font-weight: 800; line-height: 1; }
.gallery-more-sub { font-size: 0.7rem; font-weight: 500; opacity: 0.85; margin-top: 3px; }

/* ── Address / Amenities / Policies ── */
.address-row { display: flex; align-items: flex-start; gap: 8px; }
.address-text { font-size: 0.9rem; color: #475569; line-height: 1.5; }
.amenities-grid { display: flex; flex-wrap: wrap; gap: 8px; }
.amenity-chip {
  display: inline-flex; align-items: center; gap: 6px;
  background: #F1F5F9; border: 1px solid #E2E8F0;
  color: #334155; font-size: 0.8rem; font-weight: 500;
  padding: 6px 12px; border-radius: 20px;
}
.amenity-icon { font-size: 0.9rem; }
.policies-list { display: flex; flex-direction: column; gap: 10px; }
.policy-row {
  display: flex; gap: 12px;
  padding: 12px 16px; background: #F8FAFC;
  border-radius: 10px; border-left: 3px solid #6366F1;
}
.policy-label { font-size: 0.8rem; font-weight: 600; color: #64748B; min-width: 110px; flex-shrink: 0; }
.policy-value { font-size: 0.85rem; color: #334155; line-height: 1.5; }
@media (max-width: 480px) { .policy-row { flex-direction: column; gap: 4px; } }

/* ── CTA ── */
.cta-wrap { padding-top: 4px; }
.cta-btn {
  display: flex; align-items: center; justify-content: center; gap: 8px;
  width: 100%;
  background: linear-gradient(135deg, #6366F1, #8B5CF6);
  color: white; font-size: 1rem; font-weight: 700;
  padding: 16px 24px; border-radius: 14px; border: none; cursor: pointer;
  transition: opacity 0.2s, transform 0.2s, box-shadow 0.2s;
  box-shadow: 0 4px 16px rgba(99,102,241,0.4);
  font-family: 'Plus Jakarta Sans', 'Inter', sans-serif;
}
.cta-btn:hover { opacity: 0.93; transform: translateY(-2px); box-shadow: 0 8px 24px rgba(99,102,241,0.5); }
.cta-btn:active { transform: translateY(0); }

/* ── Lightbox ── */
.lightbox-overlay {
  position: fixed; inset: 0; z-index: 9000;
  background: rgba(0,0,0,0.92);
  display: flex; align-items: center; justify-content: center;
  padding: 16px;
}
.lightbox-box {
  position: relative;
  width: 100%;
  max-width: 900px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
}
.lightbox-close {
  position: absolute;
  top: -44px; right: 0;
  background: rgba(255,255,255,0.15);
  border: 1px solid rgba(255,255,255,0.25);
  color: white; font-size: 1rem;
  width: 36px; height: 36px;
  border-radius: 50%; cursor: pointer;
  display: flex; align-items: center; justify-content: center;
  transition: background 0.2s;
}
.lightbox-close:hover { background: rgba(255,255,255,0.28); }
.lightbox-counter {
  font-size: 0.78rem; font-weight: 600;
  color: rgba(255,255,255,0.65);
  letter-spacing: 0.05em;
}
.lightbox-img-wrap {
  width: 100%;
  max-height: 70vh;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 12px;
  overflow: hidden;
}
.lightbox-img {
  max-width: 100%;
  max-height: 70vh;
  width: auto;
  height: auto;
  object-fit: contain;
  border-radius: 12px;
  display: block;
}
.lightbox-caption {
  font-size: 0.85rem; color: rgba(255,255,255,0.8);
  display: flex; align-items: center; gap: 8px;
}
.lightbox-cat-badge {
  font-size: 0.7rem; font-weight: 600;
  background: rgba(99,102,241,0.6);
  color: white; padding: 2px 8px; border-radius: 12px;
}
.lightbox-nav {
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  width: 44px; height: 44px;
  border-radius: 50%;
  background: rgba(255,255,255,0.15);
  border: 1px solid rgba(255,255,255,0.2);
  display: flex; align-items: center; justify-content: center;
  cursor: pointer;
  transition: background 0.2s;
  z-index: 10;
}
.lightbox-nav:hover { background: rgba(255,255,255,0.28); }
.lightbox-prev { left: -56px; }
.lightbox-next { right: -56px; }
@media (max-width: 768px) {
  .lightbox-prev { left: 4px; }
  .lightbox-next { right: 4px; }
}
.lightbox-dots {
  display: flex; gap: 6px; flex-wrap: wrap;
  justify-content: center; max-width: 300px;
}
.lightbox-dot {
  width: 7px; height: 7px;
  border-radius: 50%;
  background: rgba(255,255,255,0.3);
  border: none; cursor: pointer; padding: 0;
  transition: background 0.2s, transform 0.2s;
}
.lightbox-dot.active { background: white; transform: scale(1.4); }

/* Lightbox transition */
.lightbox-enter-active, .lightbox-leave-active { transition: opacity 0.22s ease; }
.lightbox-enter-from, .lightbox-leave-to { opacity: 0; }

@keyframes animate-fade-in {
  from { opacity: 0; transform: translateY(12px); }
  to { opacity: 1; transform: translateY(0); }
}
.animate-fade-in { animation: animate-fade-in 0.4s ease forwards; }
</style>

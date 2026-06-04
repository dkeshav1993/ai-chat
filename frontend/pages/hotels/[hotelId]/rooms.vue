<script setup lang="ts">
import { useRoomDetails } from '~/composables/useRoomDetails'
import { useSessionId } from '~/composables/useSessionId'

const route = useRoute()
const hotelId = route.params.hotelId as string

const sessionId = ref('')

const { rooms, roomState, roomError, pgRedirectUrl, fetchRoomDetails } = useRoomDetails()

onMounted(() => {
  sessionId.value = useSessionId()
  fetchRoomDetails(hotelId, sessionId.value)
})

function handleRetry(): void {
  fetchRoomDetails(hotelId, sessionId.value)
}
</script>

<template>
  <div class="page-root">
    <div class="bg-orb bg-orb-1" />
    <div class="bg-orb bg-orb-2" />

    <!-- Header -->
    <header class="app-header">
      <div class="header-inner">
        <NuxtLink :to="`/hotels/${hotelId}`" class="back-btn">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><polyline points="15 18 9 12 15 6"/></svg>
          Back to Hotel
        </NuxtLink>
        <div class="header-brand">
          <img src="/tc-logo.png" alt="Thomas Cook India" class="tc-logo-img" />
          <div>
            <span class="brand-name">NexTrip AI</span>
            <span class="brand-sub">powered by Thomas Cook India</span>
          </div>
        </div>
      </div>
    </header>

    <!-- Content -->
    <main class="main-content">
      <div class="content-wrap">
        <!-- Page heading -->
        <div class="page-heading">
          <h1 class="page-title">Available Rooms</h1>
          <p class="page-sub">Select a room that suits your stay</p>
        </div>

        <RoomList
          :rooms="rooms"
          :room-state="roomState"
          :pg-redirect-url="pgRedirectUrl"
          :room-error="roomError"
          :hotel-id="hotelId"
          @retry="handleRetry"
        />
      </div>
    </main>
  </div>
</template>

<style scoped>
.page-root {
  min-height: 100vh;
  background: var(--app-bg);
  position: relative;
  overflow-x: hidden;
}
.bg-orb {
  position: fixed;
  border-radius: 50%;
  filter: blur(80px);
  pointer-events: none;
  z-index: 0;
}
.bg-orb-1 {
  width: 500px; height: 500px;
  background: radial-gradient(circle, rgba(245,158,11,0.08) 0%, transparent 70%);
  top: -100px; right: -100px;
}
.bg-orb-2 {
  width: 400px; height: 400px;
  background: radial-gradient(circle, rgba(99,102,241,0.08) 0%, transparent 70%);
  bottom: 0; left: -100px;
}

.app-header {
  position: sticky;
  top: 0;
  z-index: 50;
  background: rgba(10, 15, 30, 0.75);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border-bottom: 1px solid rgba(255,255,255,0.07);
}
.header-inner {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
  height: 56px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.back-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-size: 0.875rem;
  font-weight: 600;
  color: rgba(148, 163, 184, 0.9);
  text-decoration: none;
  transition: color 0.2s;
}
.back-btn:hover { color: white; }
.header-brand {
  display: flex;
  align-items: center;
  gap: 8px;
  color: white;
}
.tc-logo-img { height: 30px; width: auto; object-fit: contain; flex-shrink: 0; filter: brightness(1.05) drop-shadow(0 0 3px rgba(255,255,255,0.12)); }
.brand-name { display: block; font-size: 0.9rem; font-weight: 700; color: white; line-height: 1.1; }
.brand-sub { display: block; font-size: 0.6rem; color: rgba(148,163,184,0.8); line-height: 1; }

.main-content {
  position: relative;
  z-index: 1;
  padding: 28px 20px 60px;
}
.content-wrap {
  max-width: 1200px;
  margin: 0 auto;
}
.page-heading {
  margin-bottom: 24px;
}
.page-title {
  font-size: 1.75rem;
  font-weight: 800;
  color: white;
  margin: 0 0 6px;
  font-family: 'Plus Jakarta Sans', 'Inter', sans-serif;
}
.page-sub {
  font-size: 0.9rem;
  color: rgba(148, 163, 184, 0.8);
  margin: 0;
}

@media (max-width: 768px) {
  .main-content { padding: 16px 12px 40px; }
  .content-wrap { max-width: 100%; }
  .header-inner { padding: 0 12px !important; }
  .page-title { font-size: 1.3rem; }
}
</style>

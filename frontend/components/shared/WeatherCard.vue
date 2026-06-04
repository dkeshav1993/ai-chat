<script setup lang="ts">
export interface WeatherData {
  city: string
  temp_C: string
  feelsLike_C: string
  humidity: string
  weatherDesc: string
  weatherIconUrl?: string
  windspeedKmph: string
  winddir16Point?: string
  uvIndex: string
  visibility: string
  cloudcover: string
  pressure?: string
  precipMM?: string
}

interface Props {
  weather: WeatherData
  city: string
}

const props = defineProps<Props>()

const tempNum = computed(() => parseInt(props.weather.temp_C) || 0)
const desc = computed(() => (props.weather.weatherDesc || '').toLowerCase())

const isSunny = computed(() => desc.value.includes('sun') || desc.value.includes('clear'))
const isRainy = computed(() => desc.value.includes('rain') || desc.value.includes('drizzle') || desc.value.includes('shower'))
const isSnowy = computed(() => desc.value.includes('snow') || desc.value.includes('blizzard'))
const isThunder = computed(() => desc.value.includes('thunder') || desc.value.includes('storm'))

const weatherClass = computed(() => {
  if (isSunny.value && tempNum.value > 30) return 'wc-hot'
  if (isSunny.value) return 'wc-sunny'
  if (isRainy.value || isThunder.value) return 'wc-rainy'
  if (isSnowy.value) return 'wc-snowy'
  return 'wc-cloudy'
})

const emoji = computed(() => {
  if (isThunder.value) return '⛈️'
  if (isSnowy.value) return '❄️'
  if (isRainy.value) return '🌧️'
  if (isSunny.value && tempNum.value > 35) return '🔥'
  if (isSunny.value) return '☀️'
  const d = desc.value
  if (d.includes('overcast')) return '☁️'
  if (d.includes('fog') || d.includes('mist')) return '🌫️'
  return '⛅'
})

const travelTip = computed(() => {
  const t = tempNum.value
  if (isThunder.value) return '⚡ Thunderstorms — book a cozy indoor hotel!'
  if (isSnowy.value) return '❄️ Snowfall expected — pack warm layers.'
  if (isRainy.value) return '☂️ Rainy day — great for a luxe indoor stay.'
  if (t > 35) return '🔥 Very hot! Look for hotels with a pool.'
  if (t > 28) return '🌤️ Warm & pleasant — perfect for exploring.'
  if (t > 15) return '😊 Comfortable — great weather for sightseeing!'
  return '🧥 Cool weather — pack a jacket for evenings.'
})

const uvRisk = computed(() => {
  const uv = parseInt(props.weather.uvIndex) || 0
  if (uv >= 8) return { label: 'High', color: '#EA580C' }
  if (uv >= 3) return { label: 'Moderate', color: '#65A30D' }
  return { label: 'Low', color: '#16A34A' }
})

// Subtle animated bg particles
function rainStyle(i: number) {
  return {
    left: `${(i * 9) % 100}%`,
    animationDelay: `${(i * 0.2) % 1.5}s`,
    animationDuration: `${0.6 + (i * 0.08) % 0.4}s`,
  }
}
function rayStyle(i: number) {
  return { transform: `rotate(${i * 45}deg)`, animationDelay: `${i * 0.15}s` }
}
</script>

<template>
  <div class="weather-card" :class="weatherClass">
    <!-- Subtle animated background -->
    <div class="wc-bg-anim" aria-hidden="true">
      <template v-if="isRainy || isThunder">
        <div v-for="i in 10" :key="i" class="rain-drop" :style="rainStyle(i)" />
      </template>
      <template v-else-if="isSunny">
        <div class="sun-glow" />
        <div v-for="i in 6" :key="i" class="sun-ray" :style="rayStyle(i)" />
      </template>
    </div>

    <!-- Scanning overlay -->
    <!-- (scanning overlay removed — use chat messages for status) -->

    <!-- Compact horizontal layout -->
    <div class="wc-content">
      <!-- Left: emoji + temp + city -->
      <div class="wc-left">
        <span class="wc-emoji">{{ emoji }}</span>
        <div class="wc-temp-block">
          <span class="wc-temp-big">{{ weather.temp_C }}<span class="wc-deg">°C</span></span>
          <span class="wc-feels">Feels {{ weather.feelsLike_C }}°C</span>
        </div>
        <div class="wc-city-block">
          <span class="wc-city-name">{{ city }}</span>
          <span class="wc-desc">{{ weather.weatherDesc }}</span>
        </div>
      </div>

      <!-- Right: 4 stat chips in 2×2 grid -->
      <div class="wc-stats">
        <div class="wc-stat">
          <span>💧</span>
          <span class="wc-sv">{{ weather.humidity }}%</span>
          <span class="wc-sl">Humidity</span>
        </div>
        <div class="wc-stat">
          <span>💨</span>
          <span class="wc-sv">{{ weather.windspeedKmph }}<small> km/h</small></span>
          <span class="wc-sl">Wind</span>
        </div>
        <div class="wc-stat">
          <span>🌞</span>
          <span class="wc-sv" :style="{ color: uvRisk.color }">UV {{ weather.uvIndex }}</span>
          <span class="wc-sl">{{ uvRisk.label }}</span>
        </div>
        <div class="wc-stat">
          <span>👁️</span>
          <span class="wc-sv">{{ weather.visibility }}<small> km</small></span>
          <span class="wc-sl">Visibility</span>
        </div>
      </div>
    </div>

    <!-- Travel tip (single line) -->
    <div class="wc-tip">{{ travelTip }}</div>
  </div>
</template>

<style scoped>
.weather-card {
  position: relative;
  border-radius: 16px;
  overflow: hidden;
  padding: 14px 16px 12px;
  color: white;
  border: 1px solid rgba(255,255,255,0.12);
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.wc-hot    { background: linear-gradient(135deg, #92400e 0%, #dc2626 100%); }
.wc-sunny  { background: linear-gradient(135deg, #1e3a5f 0%, #0ea5e9 100%); }
.wc-rainy  { background: linear-gradient(135deg, #1e293b 0%, #475569 100%); }
.wc-snowy  { background: linear-gradient(135deg, #1e3a5f 0%, #3b82f6 100%); }
.wc-cloudy { background: linear-gradient(135deg, #1e2d3d 0%, #374151 100%); }

/* Compact horizontal layout */
.wc-content {
  position: relative; z-index: 1;
  display: flex; align-items: center; gap: 14px;
}

.wc-left {
  display: flex; align-items: center; gap: 10px; flex-shrink: 0;
}

.wc-emoji { font-size: 1.8rem; animation: bob 3s ease-in-out infinite; }
@keyframes bob { 0%, 100% { transform: translateY(0); } 50% { transform: translateY(-4px); } }

.wc-temp-block { display: flex; flex-direction: column; align-items: flex-end; }
.wc-temp-big { font-size: 2rem; font-weight: 900; color: white; line-height: 1; }
.wc-deg { font-size: 1.1rem; font-weight: 400; }
.wc-feels { font-size: 0.68rem; color: rgba(255,255,255,0.65); white-space: nowrap; }

.wc-city-block { display: flex; flex-direction: column; border-left: 1px solid rgba(255,255,255,0.2); padding-left: 10px; }
.wc-city-name { font-size: 0.95rem; font-weight: 800; color: white; white-space: nowrap; }
.wc-desc { font-size: 0.7rem; color: rgba(255,255,255,0.65); text-transform: capitalize; white-space: nowrap; }

/* 2×2 stats grid */
.wc-stats {
  display: grid; grid-template-columns: 1fr 1fr; gap: 6px; flex: 1; min-width: 0;
}
.wc-stat {
  background: rgba(255,255,255,0.1); border: 1px solid rgba(255,255,255,0.12);
  border-radius: 8px; padding: 5px 8px;
  display: flex; flex-direction: column; align-items: center; gap: 1px;
}
.wc-sv { font-size: 0.78rem; font-weight: 700; color: white; }
.wc-sv small { font-size: 0.62rem; font-weight: 400; opacity: 0.8; }
.wc-sl { font-size: 0.62rem; color: rgba(255,255,255,0.6); }

/* Travel tip */
.wc-tip {
  position: relative; z-index: 1;
  background: rgba(0,0,0,0.18); border: 1px solid rgba(255,255,255,0.1);
  border-radius: 8px; padding: 7px 12px;
  font-size: 0.76rem; color: rgba(255,255,255,0.88); line-height: 1.4;
}

.fade-enter-active, .fade-leave-active { transition: opacity 0.3s; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
</style>

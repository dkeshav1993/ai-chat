<script setup lang="ts">
import type { SseErrorEvent } from '~/types/sse'

interface Props {
  error: SseErrorEvent
}

const props = defineProps<Props>()
const emit = defineEmits<{
  retry: []
}>()
</script>

<template>
  <div class="flex flex-col items-center justify-center gap-5 py-14 px-6 text-center animate-fade-in">
    <div class="error-icon">
      <svg width="48" height="48" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
        <circle cx="12" cy="12" r="10" stroke="#EF4444" stroke-width="1.5" fill="rgba(239,68,68,0.1)"/>
        <path d="M12 8v5" stroke="#EF4444" stroke-width="2" stroke-linecap="round"/>
        <circle cx="12" cy="16" r="1" fill="#EF4444"/>
      </svg>
    </div>
    <div>
      <h3 class="text-lg font-semibold text-red-400 mb-2">Something went wrong</h3>
      <p class="text-sm text-slate-400 max-w-sm leading-relaxed">{{ props.error.message }}</p>
    </div>
    <button
      v-if="props.error.recoverable"
      class="btn-retry"
      @click="emit('retry')"
    >
      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"><polyline points="1 4 1 10 7 10"/><path d="M3.51 15a9 9 0 1 0 .49-3.5"/></svg>
      Try Again
    </button>
  </div>
</template>

<style scoped>
.btn-retry {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  background: linear-gradient(135deg, #6366F1, #8B5CF6);
  color: white;
  font-weight: 600;
  font-size: 0.875rem;
  padding: 10px 22px;
  border-radius: 10px;
  border: none;
  cursor: pointer;
  transition: opacity 0.2s, transform 0.2s;
}
.btn-retry:hover {
  opacity: 0.9;
  transform: translateY(-1px);
}
.btn-retry:active {
  transform: translateY(0);
}
</style>

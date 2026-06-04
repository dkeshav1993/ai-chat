<script setup lang="ts">
interface Props {
  disabled?: boolean
  history?: string[]
}

const props = defineProps<Props>()
const emit = defineEmits<{
  submit: [query: string]
}>()

const query = ref('')
const isListening = ref(false)
let recognition: any = null
let autoSendTimer: ReturnType<typeof setTimeout> | null = null

// ── Keyboard history navigation ───────────────────────────────────────────────
const historyIndex = ref(-1)   // -1 = "current draft"
const draftText = ref('')       // saves unsent draft when navigating

function handleSubmit(): void {
  const trimmed = query.value.trim()
  if (!trimmed || props.disabled) return
  if (autoSendTimer) { clearTimeout(autoSendTimer); autoSendTimer = null }
  historyIndex.value = -1
  draftText.value = ''
  emit('submit', trimmed)
  query.value = ''
  stopMic()
  nextTick(() => autoResizeTextarea())
}

function handleKeydown(e: KeyboardEvent): void {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault()
    handleSubmit()
    return
  }

  const hist = props.history || []
  if (e.key === 'ArrowUp' && hist.length > 0) {
    e.preventDefault()
    if (historyIndex.value === -1) {
      draftText.value = query.value
      historyIndex.value = 0
    } else if (historyIndex.value < hist.length - 1) {
      historyIndex.value++
    }
    query.value = hist[hist.length - 1 - historyIndex.value] || ''
    nextTick(() => autoResizeTextarea())
    return
  }

  if (e.key === 'ArrowDown' && historyIndex.value >= 0) {
    e.preventDefault()
    if (historyIndex.value === 0) {
      historyIndex.value = -1
      query.value = draftText.value
    } else {
      historyIndex.value--
      query.value = hist[hist.length - 1 - historyIndex.value] || ''
    }
    nextTick(() => autoResizeTextarea())
  }
}

// ── Auto-resize textarea ──────────────────────────────────────────────────────
const textareaRef = ref<HTMLTextAreaElement | null>(null)

function autoResizeTextarea(): void {
  const el = textareaRef.value
  if (!el) return
  el.style.height = 'auto'
  el.style.height = Math.min(el.scrollHeight, 140) + 'px'
}

function getSpeechRecognition(): any {
  if (process.client) {
    return (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition || null
  }
  return null
}

// Normalize common STT misrecognitions for spoken commands
function normalizeSpeechText(text: string): string {
  return text
    // ── Command word fixes ────────────────────────────────────────────────────
    .replace(/\bre[\s\-]set\b/gi, 'reset')         // "re set" / "re-set" → "reset"
    .replace(/\bre[\s\-]sets\b/gi, 'resets')
    .replace(/\bclear\s+all\b/gi, 'clear all')      // spacing normalise
    .replace(/\bfil\s*ter\b/gi, 'filter')           // "fil ter" → "filter"
    .replace(/\bfil\s*ters\b/gi, 'filters')
    // ── Budget / price ────────────────────────────────────────────────────────
    .replace(/\bmin(?:imum)?\s+bud\s*get\b/gi, 'min budget')
    .replace(/\bmax(?:imum)?\s+bud\s*get\b/gi, 'max budget')
    .replace(/\bbud\s*get\b/gi, 'budget')
    .replace(/\bmaximum\b/gi, 'maximum')
    .replace(/\bminimum\b/gi, 'minimum')
    // ── Star rating ───────────────────────────────────────────────────────────
    .replace(/\bstar\s+rat\s*ing\b/gi, 'star rating')
    .replace(/\brat\s*ing\b/gi, 'rating')
    // ── Hotel name ────────────────────────────────────────────────────────────
    .replace(/\bho\s*tel\b/gi, 'hotel')
    .trim()
}

function stopMic(): void {
  if (recognition) {
    recognition.onresult = null
    recognition.onerror = null
    recognition.onend = null
    try { recognition.stop() } catch {}
    recognition = null
  }
  if (autoSendTimer) { clearTimeout(autoSendTimer); autoSendTimer = null }
  isListening.value = false
}

function scheduleAutoSend(): void {
  if (autoSendTimer) clearTimeout(autoSendTimer)
  autoSendTimer = setTimeout(() => {
    autoSendTimer = null
    stopMic()
    if (query.value.trim()) handleSubmit()
  }, 2000)
}

function toggleMic(): void {
  if (isListening.value) {
    stopMic()
    return
  }
  const SR = getSpeechRecognition()
  if (!SR) {
    alert('Speech recognition is not supported in this browser. Try Chrome or Edge.')
    return
  }

  recognition = new SR()
  recognition.lang = 'en-US'
  recognition.interimResults = true
  // continuous=true prevents the browser stopping on pause mid-sentence
  recognition.continuous = true
  recognition.maxAlternatives = 1

  recognition.onresult = (e: any) => {
    // Rebuild transcript: accumulate all final parts + current interim part
    let finalText = ''
    let interimText = ''
    for (let i = 0; i < e.results.length; i++) {
      const text = e.results[i][0].transcript
      if (e.results[i].isFinal) {
        finalText += text + ' '
      } else {
        interimText += text
      }
    }
    const combined = normalizeSpeechText((finalText + interimText).trim())
    query.value = combined
    nextTick(() => autoResizeTextarea())

    // Any final result resets the auto-send countdown
    if (finalText.trim()) {
      scheduleAutoSend()
    }
  }

  recognition.onerror = (e: any) => {
    // 'no-speech' is normal silence — ignore it, don't stop
    if (e.error === 'no-speech') return
    // Any real error: clean up fully
    stopMic()
  }

  recognition.onend = () => {
    // If we're still supposed to be listening (unexpected browser auto-stop),
    // restart the recognition once so it doesn't hang silently
    if (isListening.value && recognition) {
      try {
        recognition.start()
        return
      } catch {
        // Can't restart — fall through to cleanup
      }
    }
    isListening.value = false
    // Ended without a final result but text is in the box → still auto-send
    if (query.value.trim() && !autoSendTimer) {
      scheduleAutoSend()
    }
  }

  try {
    recognition.start()
    isListening.value = true
  } catch {
    recognition = null
    isListening.value = false
    alert('Could not start speech recognition. Please check microphone permissions.')
  }
}

onBeforeUnmount(() => {
  stopMic()
  if (autoSendTimer) clearTimeout(autoSendTimer)
})
</script>

<template>
  <div class="input-row">
    <div class="input-wrap" :class="{ 'input-disabled': props.disabled }">
      <!-- Decorative icon -->
      <div class="input-icon">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
          <path d="M12 2a3 3 0 0 0-3 3v7a3 3 0 0 0 6 0V5a3 3 0 0 0-3-3z"/>
          <path d="M19 10v2a7 7 0 0 1-14 0v-2"/>
          <line x1="12" y1="19" x2="12" y2="22"/>
          <line x1="8" y1="22" x2="16" y2="22"/>
        </svg>
      </div>

      <textarea
        ref="textareaRef"
        v-model="query"
        rows="1"
        placeholder="e.g. Find me a 5-star hotel in Goa from Dec 20 to Dec 25 for 2 adults"
        :disabled="props.disabled"
        class="input-textarea"
        @keydown="handleKeydown"
        @input="autoResizeTextarea"
      />

      <!-- Mic button -->
      <button
        type="button"
        class="mic-btn"
        :class="{ 'mic-active': isListening }"
        :title="isListening ? 'Stop listening' : 'Speak your search (English)'"
        @click="toggleMic"
      >
        <svg v-if="!isListening" width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M12 2a3 3 0 0 0-3 3v7a3 3 0 0 0 6 0V5a3 3 0 0 0-3-3z"/>
          <path d="M19 10v2a7 7 0 0 1-14 0v-2"/>
          <line x1="12" y1="19" x2="12" y2="22"/>
        </svg>
        <svg v-else width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round">
          <rect x="6" y="4" width="4" height="16" rx="1"/>
          <rect x="14" y="4" width="4" height="16" rx="1"/>
        </svg>
      </button>

      <!-- Send button -->
      <button
        type="button"
        :disabled="props.disabled || !query.trim()"
        class="send-btn"
        @click="handleSubmit"
      >
        <svg v-if="!props.disabled" width="18" height="18" viewBox="0 0 24 24" fill="none">
          <path d="M22 2L11 13" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/>
          <path d="M22 2L15 22L11 13L2 9L22 2Z" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
        <svg v-else width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round">
          <rect x="6" y="6" width="12" height="12" rx="2"/>
        </svg>
      </button>
    </div>
  </div>
</template>

<style scoped>
.input-row {
  padding: 4px 0;
  display: flex;
  align-items: flex-end;
  width: 100%;
}

.input-wrap {
  display: flex;
  align-items: flex-end;
  gap: 6px;
  flex: 1;
  min-width: 0;
  background: rgba(255, 255, 255, 0.06);
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: 16px;
  padding: 8px 8px 8px 14px;
  transition: border-color 0.2s, box-shadow 0.2s;
}
.input-wrap:focus-within {
  border-color: rgba(99, 102, 241, 0.6);
  box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.12);
}
.input-disabled {
  opacity: 0.6;
  pointer-events: none;
}

.input-icon {
  color: #6366F1;
  flex-shrink: 0;
  padding-bottom: 2px;
}

.input-textarea {
  flex: 1;
  background: transparent;
  border: none;
  outline: none;
  resize: none;
  color: #E2E8F0;
  font-family: 'Inter', system-ui, sans-serif;
  font-size: 0.875rem;
  line-height: 1.55;
  min-height: 24px;
  max-height: 140px;
  overflow-y: auto;
  word-break: break-word;
  white-space: pre-wrap;
}
.input-textarea::placeholder {
  color: rgba(148, 163, 184, 0.7);
}

/* Mic button */
.mic-btn {
  flex-shrink: 0;
  width: 32px;
  height: 32px;
  border-radius: 8px;
  background: rgba(255,255,255,0.07);
  border: 1px solid rgba(255,255,255,0.12);
  color: rgba(148,163,184,0.8);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background 0.2s, color 0.2s, border-color 0.2s;
  margin-bottom: 2px;
}
.mic-btn:hover {
  background: rgba(99,102,241,0.15);
  border-color: rgba(99,102,241,0.35);
  color: #818CF8;
}
.mic-btn.mic-active {
  background: rgba(239,68,68,0.2);
  border-color: rgba(239,68,68,0.5);
  color: #F87171;
  animation: mic-pulse 1.2s ease-in-out infinite;
}
@keyframes mic-pulse {
  0%, 100% { box-shadow: 0 0 0 0 rgba(239,68,68,0.4); }
  50% { box-shadow: 0 0 0 6px rgba(239,68,68,0); }
}

.send-btn {
  flex-shrink: 0;
  width: 36px;
  height: 36px;
  border-radius: 10px;
  background: linear-gradient(135deg, #6366F1, #8B5CF6);
  color: white;
  border: none;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: opacity 0.2s, transform 0.15s;
  margin-bottom: 0px;
}
.send-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}
.send-btn:not(:disabled):hover {
  opacity: 0.9;
  transform: scale(1.05);
}
.send-btn:not(:disabled):active {
  transform: scale(0.97);
}
</style>

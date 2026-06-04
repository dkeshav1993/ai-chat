<script setup lang="ts">
interface Props {
  role: 'user' | 'assistant' | 'thinking'
  content: string
}

const props = defineProps<Props>()

// Simple inline markdown → HTML (bold, italic, newlines)
function renderMarkdown(text: string): string {
  return text
    .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
    .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.+?)\*/g, '<em>$1</em>')
    .replace(/\n/g, '<br/>')
}
</script>

<template>
  <div
    class="flex items-end gap-3 mb-4 animate-fade-in"
    :class="props.role === 'user' ? 'flex-row-reverse' : 'flex-row'"
  >
    <!-- Avatar -->
    <div
      class="avatar shrink-0"
      :class="props.role === 'user' ? 'avatar-user' : 'avatar-ai'"
    >
      <!-- User avatar: person silhouette -->
      <svg v-if="props.role === 'user'" viewBox="0 0 32 32" fill="none" xmlns="http://www.w3.org/2000/svg" width="18" height="18">
        <circle cx="16" cy="12" r="5.5" fill="white" opacity="0.95"/>
        <path d="M5 29c0-6.075 4.925-11 11-11s11 4.925 11 11" fill="white" opacity="0.85"/>
      </svg>
      <!-- Donna avatar: sleek AI face looking right -->
      <svg v-else viewBox="0 0 32 32" fill="none" xmlns="http://www.w3.org/2000/svg" width="20" height="20">
        <!-- Face circle -->
        <circle cx="16" cy="15" r="9" stroke="rgba(255,255,255,0.9)" stroke-width="1.2" fill="none"/>
        <!-- Right eye (main, looking right) -->
        <circle cx="18.5" cy="13.5" r="2" fill="rgba(255,255,255,0.95)"/>
        <circle cx="19.3" cy="13" r="0.9" fill="#6366F1"/>
        <circle cx="19.7" cy="12.6" r="0.35" fill="white"/>
        <!-- Left eye (slightly smaller) -->
        <circle cx="13.5" cy="14" r="1.5" fill="rgba(255,255,255,0.85)"/>
        <circle cx="14.1" cy="13.5" r="0.65" fill="#6366F1"/>
        <!-- Smile -->
        <path d="M12.5 18.5 Q16 21.5 19.5 18.5" stroke="rgba(255,255,255,0.85)" stroke-width="1" fill="none" stroke-linecap="round"/>
        <!-- Antenna -->
        <line x1="16" y1="6" x2="16" y2="3.5" stroke="rgba(255,255,255,0.75)" stroke-width="1.1" stroke-linecap="round"/>
        <circle cx="16" cy="3" r="1.1" fill="rgba(255,255,255,0.75)"/>
      </svg>
    </div>

    <!-- Bubble -->
    <div
      v-if="props.role === 'thinking'"
      class="bubble bubble-thinking"
    >
      <span class="dot" style="animation-delay: 0ms" />
      <span class="dot" style="animation-delay: 200ms" />
      <span class="dot" style="animation-delay: 400ms" />
      <span class="thinking-text">{{ props.content }}</span>
    </div>

    <div
      v-else-if="props.role === 'user'"
      class="bubble bubble-user"
    >
      {{ props.content }}
    </div>

    <div
      v-else
      class="bubble bubble-ai"
      v-html="renderMarkdown(props.content)"
    />
  </div>
</template>

<style scoped>
.avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.75rem;
  font-weight: 700;
  flex-shrink: 0;
}
.avatar-user {
  background: linear-gradient(135deg, #6366F1, #8B5CF6);
  color: white;
}
.avatar-ai {
  background: rgba(99, 102, 241, 0.15);
  border: 1px solid rgba(99, 102, 241, 0.3);
  color: #818CF8;
}

.bubble {
  max-width: min(80%, 480px);
  padding: 11px 16px;
  border-radius: 18px;
  font-size: 0.875rem;
  line-height: 1.6;
}
.bubble-user {
  background: linear-gradient(135deg, #6366F1, #8B5CF6);
  color: white;
  border-bottom-right-radius: 4px;
}
.bubble-ai {
  background: rgba(255, 255, 255, 0.06);
  border: 1px solid rgba(255, 255, 255, 0.1);
  color: #E2E8F0;
  border-bottom-left-radius: 4px;
}
.bubble-thinking {
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.08);
  color: #94A3B8;
  border-bottom-left-radius: 4px;
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 10px 14px;
}

.dot {
  display: inline-block;
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: #6366F1;
  animation: bounce 1.4s ease-in-out infinite;
  flex-shrink: 0;
}
@keyframes bounce {
  0%, 60%, 100% { transform: translateY(0); }
  30% { transform: translateY(-6px); }
}

.thinking-text {
  font-size: 0.8125rem;
  font-style: italic;
}
</style>

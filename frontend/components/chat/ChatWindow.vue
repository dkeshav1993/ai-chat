<script setup lang="ts">
import type { ConversationalTurn } from '~/composables/useChat'

interface Props {
  turns: ConversationalTurn[]
}

const props = defineProps<Props>()
const chatScrollEl = ref<HTMLElement | null>(null)
const scrollAnchor = ref<HTMLElement | null>(null)

function scrollToBottom() {
  if (chatScrollEl.value) {
    chatScrollEl.value.scrollTop = chatScrollEl.value.scrollHeight
  }
}

function isNearBottom(): boolean {
  const el = chatScrollEl.value
  if (!el) return true
  return el.scrollHeight - el.scrollTop - el.clientHeight <= 120
}

// ── New message added (turns.length increases) → always scroll to bottom ──
// This fires when DONNA or the user sends a new message.
watch(
  () => props.turns.length,
  async () => {
    await nextTick()
    scrollToBottom()
  }
)

// ── Existing message content updated (e.g. streaming text update) →
//    only scroll if the user is already near the bottom (they haven't scrolled up) ──
watch(
  () => props.turns.map(t => t.content).join(''),
  async () => {
    await nextTick()
    if (isNearBottom()) scrollToBottom()
  }
)
</script>

<template>
  <div ref="chatScrollEl" class="chat-scroll flex-1 overflow-y-auto px-4 pt-4 pb-2">
    <ChatBubble
      v-for="(turn, index) in props.turns"
      :key="index"
      :role="turn.role"
      :content="turn.content"
    />
    <div ref="scrollAnchor" />
  </div>
</template>

<style scoped>
.chat-scroll {
  scrollbar-width: thin;
  scrollbar-color: rgba(99, 102, 241, 0.3) transparent;
}
</style>

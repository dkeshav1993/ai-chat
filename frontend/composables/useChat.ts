import { ref } from 'vue'

export interface ConversationalTurn {
  role: 'user' | 'assistant' | 'thinking'
  content: string
  timestamp: number
}

const SESSION_KEY = 'nextrip:chat:turns'

// ─── Singleton state (shared across all useChat() calls in the same app) ──────
const _turns = ref<ConversationalTurn[]>(_loadTurns())

function _loadTurns(): ConversationalTurn[] {
  if (typeof window === 'undefined') return []
  try {
    const raw = sessionStorage.getItem(SESSION_KEY)
    if (!raw) return []
    const parsed = JSON.parse(raw) as ConversationalTurn[]
    // Drop any stale thinking turns from previous sessions
    return parsed.filter((t) => t.role !== 'thinking')
  } catch {
    return []
  }
}

function _saveTurns(turns: ConversationalTurn[]): void {
  if (typeof window === 'undefined') return
  try {
    // Don't persist thinking turns
    const toSave = turns.filter((t) => t.role !== 'thinking')
    sessionStorage.setItem(SESSION_KEY, JSON.stringify(toSave))
  } catch { /* storage quota exceeded — silently skip */ }
}

export function clearChatSession(): void {
  _turns.value = []
  if (typeof window !== 'undefined') {
    sessionStorage.removeItem(SESSION_KEY)
    // Also clear hotel search session cache
    sessionStorage.removeItem('nextrip:hotels')
    sessionStorage.removeItem('nextrip:searchState')
  }
}

export function useChat() {
  function addUserTurn(content: string): void {
    _turns.value = [
      ..._turns.value,
      { role: 'user', content, timestamp: Date.now() },
    ]
    _saveTurns(_turns.value)
  }

  function addAssistantTurn(content: string): void {
    _turns.value = [
      ..._turns.value,
      { role: 'assistant', content, timestamp: Date.now() },
    ]
    _saveTurns(_turns.value)
  }

  function addThinkingTurn(content: string): void {
    const withoutThinking = _turns.value.filter((t) => t.role !== 'thinking')
    _turns.value = [
      ...withoutThinking,
      { role: 'thinking', content, timestamp: Date.now() },
    ]
    // Don't persist thinking turns
  }

  function clearThinking(): void {
    _turns.value = _turns.value.filter((t) => t.role !== 'thinking')
    _saveTurns(_turns.value)
  }

  return {
    turns: _turns,
    addUserTurn,
    addAssistantTurn,
    addThinkingTurn,
    clearThinking,
  }
}

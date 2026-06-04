import { generateCorrelationId } from '~/utils/correlationId'

const SESSION_KEY = 'nextrip_session_id'

/**
 * Returns a stable session ID that persists in localStorage for the entire
 * browsing session. All pages (search → hotel detail → rooms) use the same ID
 * so Redis can resolve searchKey across navigations.
 */
export function useSessionId(): string {
  if (!process.client) return ''
  let id = localStorage.getItem(SESSION_KEY)
  if (!id) {
    id = generateCorrelationId()
    localStorage.setItem(SESSION_KEY, id)
  }
  return id
}

export function resetSessionId(): void {
  if (!process.client) return
  const id = generateCorrelationId()
  localStorage.setItem(SESSION_KEY, id)
}

/**
 * Generate a RFC 4122-compliant UUID v4 correlation ID.
 * Uses the native Web Crypto API — no library dependency.
 */
export function generateCorrelationId(): string {
  return crypto.randomUUID()
}

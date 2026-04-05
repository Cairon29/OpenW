export function formatTime(isoString: string): string {
  if (!isoString) return ""
  try {
    const date = new Date(isoString)
    const now = new Date()
    const diffMs = now.getTime() - date.getTime()
    const diffH = diffMs / (1000 * 60 * 60)
    if (diffH < 1) return `${Math.floor(diffMs / 60000)}m`
    if (diffH < 24) return `${Math.floor(diffH)}h`
    return date.toLocaleDateString("es-CO", { day: "2-digit", month: "2-digit" })
  } catch {
    return ""
  }
}

export function getInitials(name?: string | null, phone?: string): string {
  if (name) {
    const parts = name.trim().split(/\s+/)
    if (parts.length >= 2) return (parts[0][0] + parts[1][0]).toUpperCase()
    return name.slice(0, 2).toUpperCase()
  }
  return phone?.slice(-2) ?? "??"
}

// Country codes that are 1 digit long (NANP)
const ONE_DIGIT_CODES = new Set(["1"])

// Country codes that are 3 digits long (subset of common ones)
const THREE_DIGIT_CODES = new Set([
  "375", "380", "381", "382", "385", "386", "387", "389",
  "420", "421", "423",
])

/**
 * Formats a raw E.164 phone number (digits only, no +) into a readable string.
 * Example: "573160429080" → "+57 3160429080"
 */
export function formatPhone(phone: string): string {
  if (!phone) return ""

  const threeDigit = phone.slice(0, 3)
  if (THREE_DIGIT_CODES.has(threeDigit)) {
    return `+${threeDigit} ${phone.slice(3)}`
  }

  if (ONE_DIGIT_CODES.has(phone[0]) && phone.length === 11) {
    return `+1 ${phone.slice(1)}`
  }

  // Default: assume 2-digit country code (covers most LATAM + Europe)
  return `+${phone.slice(0, 2)} ${phone.slice(2)}`
}

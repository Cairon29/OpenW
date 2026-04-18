export type Severity = "critical" | "high" | "medium" | "low"

// ── System Configuration ──────────────────────────────────────────────────────

export type ConfigValueType = "string" | "number" | "boolean" | "json"

export type ConfigCategory =
  | "general"
  | "whatsapp"
  | "email"
  | "analysis"
  | "modules"
  | "external_apis"

export interface SystemConfig {
  id: number
  key: string
  value: string | null
  value_type: ConfigValueType
  category: ConfigCategory
  label: string
  description: string | null
  is_sensitive: boolean
  is_active: boolean
  updated_at: string | null
  updated_by: string | null
}

export type ConfigsByCategory = Partial<Record<ConfigCategory, SystemConfig[]>>

export interface ConnectionTestResult {
  service: string
  ok: boolean
  message: string
}

export interface VulnerabilityCase {
  id: string
  title: string
  description: string
  severity: Severity
  status: "open" | "in_progress" | "resolved" | "closed"
  reportedBy: string
  reportedAt: Date
  assignedTo?: string
  category: string
  keywords: string[]
  whatsappNumber: string
  lastUpdated: Date
}

export interface Category {
  id: string
  name: string
  description: string
  keywords: string[]
  createdAt: Date
  color: string
}

export interface DashboardMetrics {
  totalCases: number
  openCases: number
  resolvedToday: number
  avgResolutionTime: number
  bySeverity: {
    critical: number
    high: number
    medium: number
    low: number
    info: number
  }
  byStatus: {
    open: number
    in_progress: number
    resolved: number
    closed: number
  }
  recentTrend: {
    date: string
    count: number
  }[]
}

export interface BotMetrics {
  totalConversations: number
  conversationsTrend: number
  responseRate: number
  responseTrend: number
  satisfactionRate: number
  satisfactionRatings: number
  usageOverTime: {
    date: string
    count: number
  }[]
  effectiveness: {
    conContexto: number
    sinContexto: number
  }
}


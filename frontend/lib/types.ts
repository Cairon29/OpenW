export type Severity = "critical" | "high" | "medium" | "low"

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


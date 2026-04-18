"use client"

import { useEffect, useState } from "react"
import { getNovedades, getDashboardMetrics, getBotMetrics } from "@/lib/api"
import type { DashboardMetricsAPI, BotMetricsAPI } from "@/lib/api"
import type { VulnerabilityCase, DashboardMetrics, BotMetrics } from "@/lib/types"

export function useDashboardData() {
  const [metrics, setMetrics] = useState<DashboardMetricsAPI | null>(null)
  const [botMetrics, setBotMetrics] = useState<BotMetricsAPI | null>(null)
  const [cases, setCases] = useState<VulnerabilityCase[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    Promise.all([
      getDashboardMetrics().then(setMetrics).catch(console.error),
      getBotMetrics().then(setBotMetrics).catch(console.error),
      getNovedades().then(setCases).catch(console.error),
    ]).finally(() => setLoading(false))
  }, [])

  const severityData: DashboardMetrics["bySeverity"] = {
    critical: metrics?.bySeverity?.critica ?? 0,
    high:     metrics?.bySeverity?.alta ?? 0,
    medium:   metrics?.bySeverity?.media ?? 0,
    low:      metrics?.bySeverity?.baja ?? 0,
    info:     metrics?.bySeverity?.informativa ?? 0,
  }

  const botMetricsMapped: BotMetrics = {
    totalConversations: botMetrics?.totalConversations ?? 0,
    conversationsTrend: 0,
    responseRate:       botMetrics?.responseRate ?? 0,
    responseTrend:      0,
    satisfactionRate:   0,
    satisfactionRatings: 0,
    usageOverTime:      botMetrics?.usageOverTime ?? [],
    effectiveness: {
      conContexto: botMetrics?.effectiveness?.conContexto ?? 0,
      sinContexto: botMetrics?.effectiveness?.sinContexto ?? 0,
    },
  }

  return { metrics, botMetrics, botMetricsMapped, severityData, cases, loading }
}

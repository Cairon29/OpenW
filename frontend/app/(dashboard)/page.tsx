"use client"

import { useEffect, useState } from "react"
import { AlertTriangle, CheckCircle, ShieldAlert, MessageSquare, Bot, Activity } from "lucide-react"
import { MetricCard } from "@/components/dashboard/metric-card"
import { SeverityChart } from "@/components/dashboard/severity-chart"
import { TrendChart } from "@/components/dashboard/trend-chart"
import { RecentCases } from "@/components/dashboard/recent-cases"
import { BotMetricCard } from "@/components/dashboard/bot-metric-card"
import { BotTrendChart } from "@/components/dashboard/bot-trend-chart"
import { BotEffectivenessChart } from "@/components/dashboard/bot-effectiveness-chart"
import { getNovedades, getDashboardMetrics, getBotMetrics } from "@/lib/api"
import type { DashboardMetricsAPI, BotMetricsAPI } from "@/lib/api"
import type { VulnerabilityCase, DashboardMetrics, BotMetrics } from "@/lib/types"

export default function DashboardPage() {
  const [metrics, setMetrics] = useState<DashboardMetricsAPI | null>(null)
  const [botMetrics, setBotMetrics] = useState<BotMetricsAPI | null>(null)
  const [cases, setCases] = useState<VulnerabilityCase[]>([])

  useEffect(() => {
    getDashboardMetrics().then(setMetrics).catch(console.error)
    getBotMetrics().then(setBotMetrics).catch(console.error)
    getNovedades().then(setCases).catch(console.error)
  }, [])

  // Map backend severity keys to DashboardMetrics shape for SeverityChart
  const severityData: DashboardMetrics["bySeverity"] = {
    critical: metrics?.bySeverity?.critica ?? 0,
    high: metrics?.bySeverity?.alta ?? 0,
    medium: metrics?.bySeverity?.media ?? 0,
    low:  metrics?.bySeverity?.baja        ?? 0,
    info: metrics?.bySeverity?.informativa ?? 0,
  }

  const botMetricsMapped: BotMetrics = {
    totalConversations: botMetrics?.totalConversations ?? 0,
    conversationsTrend: 0,
    responseRate: botMetrics?.responseRate ?? 0,
    responseTrend: 0,
    satisfactionRate: 0,
    satisfactionRatings: 0,
    usageOverTime: botMetrics?.usageOverTime ?? [],
    effectiveness: {
      conContexto: botMetrics?.effectiveness?.conContexto ?? 0,
      sinContexto: botMetrics?.effectiveness?.sinContexto ?? 0,
    },
  }

  return (
    <div className="space-y-6">
      {/* SECCIÓN VULNERABILIDADES */}
      <div className="flex flex-col gap-2">
        <h1 className="text-2xl font-bold text-foreground">Dashboard</h1>
        <p className="text-muted-foreground">
          Resumen de vulnerabilidades reportadas vía WhatsApp
        </p>
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <MetricCard
          title="Total de Novedades"
          value={metrics?.totalCases ?? "—"}
          description="Registradas en el sistema"
          icon={AlertTriangle}
        />
        <MetricCard
          title="Abiertas"
          value={metrics?.openCases ?? "—"}
          description="Pendientes de resolución"
          icon={CheckCircle}
        />
        <MetricCard
          title="Resueltas Hoy"
          value={metrics?.resolvedToday ?? "—"}
          description="Cerradas en el día"
          icon={Activity}
        />
        <MetricCard
          title="Críticas Activas"
          value={metrics?.criticalOpen ?? "—"}
          description="Críticas sin resolver"
          icon={ShieldAlert}
        />
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <SeverityChart data={severityData} />
        <TrendChart data={metrics?.recentTrend ?? []} />
      </div>

      {/* SECCIÓN WHATSAPP BOT */}
      <div className="mt-12 mb-6 pt-6 border-t border-border">
        <div className="flex flex-col gap-2 mb-6">
          <h2 className="text-xl font-bold text-foreground">Métricas de WhatsApp Bot</h2>
          <p className="text-muted-foreground text-sm">
            Rendimiento y uso del asistente virtual por los clientes
          </p>
        </div>

        <div className="grid gap-4 md:grid-cols-3 mb-6">
          <BotMetricCard
            title="Conversaciones Totales"
            value={botMetrics?.totalConversations ?? "—"}
            icon={MessageSquare}
            iconColor="text-gray-400"
          />
          <BotMetricCard
            title="Mensajes Enviados por el Bot"
            value={botMetrics?.botMessages ?? "—"}
            icon={Bot}
            iconColor="text-rose-500"
            trend={
              botMetrics
                ? { value: `${botMetrics.responseRate}% de conversaciones respondidas`, isPositive: botMetrics.responseRate > 0 }
                : undefined
            }
          />
          <BotMetricCard
            title="Novedades con Categoría"
            value={botMetrics ? `${botMetrics.effectiveness.conContexto}` : "—"}
            icon={ShieldAlert}
            iconColor="text-yellow-500"
            description={
              botMetrics
                ? `${botMetrics.effectiveness.sinContexto} sin categoría asignada`
                : undefined
            }
          />
        </div>

        <div className="grid gap-6 lg:grid-cols-2">
          <BotTrendChart data={botMetricsMapped.usageOverTime} />
          <BotEffectivenessChart data={botMetricsMapped.effectiveness} />
        </div>
      </div>

      <div className="pt-6">
        <RecentCases cases={cases} />
      </div>
    </div>
  )
}

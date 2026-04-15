"use client"

import { AlertTriangle, CheckCircle, ShieldAlert, MessageSquare, Bot, Activity } from "lucide-react"
import { MetricCard } from "@/components/dashboard/metric-card"
import { SeverityChart } from "@/components/dashboard/severity-chart"
import { TrendChart } from "@/components/dashboard/trend-chart"
import { RecentCases } from "@/components/dashboard/recent-cases"
import { BotMetricCard } from "@/components/dashboard/bot-metric-card"
import { BotTrendChart } from "@/components/dashboard/bot-trend-chart"
import { BotEffectivenessChart } from "@/components/dashboard/bot-effectiveness-chart"
import { PageHeader } from "@/components/dashboard/page-header"
import { useDashboardData } from "@/hooks/use-dashboard-data"

export default function DashboardPage() {
  const { metrics, botMetrics, botMetricsMapped, severityData, cases } = useDashboardData()

  return (
    <div className="space-y-6">
      <PageHeader
        title="Dashboard"
        description="Resumen de vulnerabilidades reportadas vía WhatsApp"
      />

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
        <div className="mb-6">
          <PageHeader
            title="Métricas de WhatsApp Bot"
            description="Rendimiento y uso del asistente virtual por los clientes"
          />
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
                ? {
                    value: `${botMetrics.responseRate}% de conversaciones respondidas`,
                    isPositive: botMetrics.responseRate > 0,
                  }
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

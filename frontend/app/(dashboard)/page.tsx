"use client"

import { AlertTriangle, CheckCircle, Clock, TrendingUp, MessageSquare, Target, Star } from "lucide-react"
import { MetricCard } from "@/components/dashboard/metric-card"
import { SeverityChart } from "@/components/dashboard/severity-chart"
import { TrendChart } from "@/components/dashboard/trend-chart"
import { RecentCases } from "@/components/dashboard/recent-cases"

import { BotMetricCard } from "@/components/dashboard/bot-metric-card"
import { BotTrendChart } from "@/components/dashboard/bot-trend-chart"
import { BotEffectivenessChart } from "@/components/dashboard/bot-effectiveness-chart"

import { mockMetrics, mockCases, mockBotMetrics } from "@/lib/mock-data"

export default function DashboardPage() {
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
          title="Total de Casos"
          value={mockMetrics.totalCases}
          description="Casos registrados"
          icon={AlertTriangle}
          trend={{ value: 12, isPositive: false }}
        />
        <MetricCard
          title="Casos Abiertos"
          value={mockMetrics.openCases}
          description="Pendientes de resolución"
          icon={Clock}
        />
        <MetricCard
          title="Resueltos Hoy"
          value={mockMetrics.resolvedToday}
          description="Casos cerrados"
          icon={CheckCircle}
          trend={{ value: 25, isPositive: true }}
        />
        <MetricCard
          title="Tiempo Promedio"
          value={`${mockMetrics.avgResolutionTime}h`}
          description="De resolución"
          icon={TrendingUp}
          trend={{ value: 8, isPositive: true }}
        />
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <SeverityChart data={mockMetrics.bySeverity} />
        <TrendChart data={mockMetrics.recentTrend} />
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
            value={mockBotMetrics.totalConversations}
            icon={MessageSquare}
            iconColor="text-gray-400"
            trend={{ value: `${mockBotMetrics.conversationsTrend}% vs. período anterior`, isPositive: true }}
          />
          <BotMetricCard
            title="Tasa de Respuestas con Contexto"
            value={`${mockBotMetrics.responseRate}%`}
            icon={Target}
            iconColor="text-rose-500"
            trend={{ value: `${mockBotMetrics.responseTrend} pts vs. período anterior`, isPositive: true }}
          />
          <BotMetricCard
            title="Índice de Satisfacción"
            value={`${mockBotMetrics.satisfactionRate}%`}
            icon={Star}
            iconColor="text-yellow-500"
            description={`Basado en ${mockBotMetrics.satisfactionRatings} calificaciones`}
          />
        </div>

        <div className="grid gap-6 lg:grid-cols-2">
          <BotTrendChart data={mockBotMetrics.usageOverTime} />
          <BotEffectivenessChart data={mockBotMetrics.effectiveness} />
        </div>
      </div>

      <div className="pt-6">
        <RecentCases cases={mockCases} />
      </div>
    </div>
  )
}

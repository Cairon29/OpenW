"use client"

import {
  Bar,
  BarChart,
  Cell,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import type { DashboardMetrics } from "@/lib/types"

interface SeverityChartProps {
  data: DashboardMetrics["bySeverity"]
}

const SEVERITY_CONFIG = [
  { key: "critical",    name: "Crítica",     color: "#ef4444" },
  { key: "high",        name: "Alta",        color: "#fa8200" },
  { key: "medium",      name: "Media",       color: "#facc15" },
  { key: "low",         name: "Baja",        color: "#10b981" },
  { key: "info",        name: "Informativa", color: "#06b6d4" },
] as const

export function SeverityChart({ data }: SeverityChartProps) {
  const chartData = SEVERITY_CONFIG.map(({ key, name, color }) => ({
    name,
    value: data[key],
    color,
  }))

  return (
    <Card className="border-border bg-card">
      <CardHeader>
        <CardTitle className="text-foreground">
          Distribución por Severidad
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="h-[180px] w-full">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart
              data={chartData}
              margin={{ top: 4, right: 8, left: -24, bottom: 0 }}
            >
              <XAxis
                dataKey="name"
                tick={{ fontSize: 11, fill: "hsl(var(--muted-foreground))" }}
                axisLine={false}
                tickLine={false}
              />
              <YAxis
                allowDecimals={false}
                tick={{ fontSize: 11, fill: "hsl(var(--muted-foreground))" }}
                axisLine={false}
                tickLine={false}
              />
              <Tooltip
                cursor={{ fill: "hsl(var(--muted))", opacity: 0.4 }}
                content={({ active, payload }) => {
                  if (!active || !payload?.length) return null
                  const item = payload[0]
                  return (
                    <div className="rounded-md border border-border bg-card px-3 py-2 text-sm shadow-md">
                      <span className="font-medium text-foreground">
                        {item.payload.name}
                      </span>
                      <span className="ml-2 text-muted-foreground">
                        {item.value} casos
                      </span>
                    </div>
                  )
                }}
              />
              <Bar dataKey="value" radius={[4, 4, 0, 0]}>
                {chartData.map((entry) => (
                  <Cell key={entry.name} fill={entry.color} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>

        <ul className="mt-4 grid grid-cols-2 gap-x-4 gap-y-2 sm:grid-cols-3">
          {chartData.map((entry) => (
            <li key={entry.name} className="flex items-center gap-2 text-sm">
              <span
                className="inline-block h-2.5 w-2.5 shrink-0 rounded-full"
                style={{ backgroundColor: entry.color }}
              />
              <span className="text-muted-foreground">{entry.name}</span>
              <span className="ml-auto font-medium text-foreground tabular-nums">
                {entry.value}
              </span>
            </li>
          ))}
        </ul>
      </CardContent>
    </Card>
  )
}

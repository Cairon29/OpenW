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
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/layout/card"

interface SeverityData {
  critical: number
  high: number
  medium: number
  low: number
}

interface ReportsSeverityChartProps {
  data: SeverityData
}

const SEVERITY_CONFIG = [
  { key: "critical" as const, name: "Crítica",  color: "#ef4444" },
  { key: "high"     as const, name: "Alta",     color: "#fa8200" },
  { key: "medium"   as const, name: "Media",    color: "#facc15" },
  { key: "low"      as const, name: "Baja",     color: "#10b981" },
]

export function ReportsSeverityChart({ data }: ReportsSeverityChartProps) {
  const chartData = SEVERITY_CONFIG.map(({ key, name, color }) => ({
    name,
    value: data[key],
    color,
  }))

  const total = chartData.reduce((sum, d) => sum + d.value, 0)

  return (
    <Card className="border-border bg-card">
      <CardHeader>
        <CardTitle className="text-foreground">Distribución por Severidad</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="h-[200px] w-full">
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
                  const pct = total > 0 ? Math.round(((item.value as number) / total) * 100) : 0
                  return (
                    <div className="rounded-md border border-border bg-card px-3 py-2 text-sm shadow-md">
                      <span className="font-medium text-foreground">{item.payload.name}</span>
                      <span className="ml-2 text-muted-foreground">
                        {item.value} casos ({pct}%)
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

        <ul className="mt-4 grid grid-cols-2 gap-x-4 gap-y-2">
          {chartData.map((entry) => {
            const pct = total > 0 ? Math.round((entry.value / total) * 100) : 0
            return (
              <li key={entry.name} className="flex items-center gap-2 text-sm">
                <span
                  className="inline-block h-2.5 w-2.5 shrink-0 rounded-full"
                  style={{ backgroundColor: entry.color }}
                />
                <span className="text-muted-foreground">{entry.name}</span>
                <span className="ml-auto font-medium text-foreground tabular-nums">
                  {entry.value}
                  <span className="text-muted-foreground font-normal ml-1">({pct}%)</span>
                </span>
              </li>
            )
          })}
        </ul>
      </CardContent>
    </Card>
  )
}

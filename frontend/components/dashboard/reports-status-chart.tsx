"use client"

import { Cell, Pie, PieChart, ResponsiveContainer, Tooltip } from "recharts"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/layout/card"

interface StatusData {
  open: number
  in_progress: number
  resolved: number
  closed: number
}

interface ReportsStatusChartProps {
  data: StatusData
}

const STATUS_CONFIG = [
  { key: "open"        as const, name: "Abierta",    color: "#3b82f6" },
  { key: "in_progress" as const, name: "En proceso", color: "#facc15" },
  { key: "resolved"    as const, name: "Resuelta",   color: "#10b981" },
  { key: "closed"      as const, name: "Descartada", color: "#6b7280" },
]

export function ReportsStatusChart({ data }: ReportsStatusChartProps) {
  const chartData = STATUS_CONFIG.map(({ key, name, color }) => ({
    name,
    value: data[key],
    color,
  })).filter((d) => d.value > 0)

  const total = chartData.reduce((sum, d) => sum + d.value, 0)

  return (
    <Card className="border-border bg-card">
      <CardHeader>
        <CardTitle className="text-foreground">Distribución por Estado</CardTitle>
      </CardHeader>
      <CardContent>
        {total === 0 ? (
          <div className="flex h-[200px] items-center justify-center text-muted-foreground text-sm">
            Sin datos para mostrar
          </div>
        ) : (
          <>
            <div className="relative h-[200px] w-full">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={chartData}
                    cx="50%"
                    cy="50%"
                    innerRadius={55}
                    outerRadius={85}
                    paddingAngle={3}
                    dataKey="value"
                    stroke="none"
                  >
                    {chartData.map((entry) => (
                      <Cell key={entry.name} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip
                    content={({ active, payload }) => {
                      if (!active || !payload?.length) return null
                      const item = payload[0].payload as { name: string; value: number }
                      const pct = Math.round((item.value / total) * 100)
                      return (
                        <div className="rounded-md border border-border bg-card px-3 py-2 text-sm shadow-md">
                          <span className="font-medium text-foreground">{item.name}</span>
                          <span className="ml-2 text-muted-foreground">
                            {item.value} ({pct}%)
                          </span>
                        </div>
                      )
                    }}
                  />
                </PieChart>
              </ResponsiveContainer>
              {/* Center label */}
              <div className="pointer-events-none absolute inset-0 flex flex-col items-center justify-center">
                <span className="text-2xl font-bold text-foreground">{total}</span>
                <span className="text-xs text-muted-foreground">total</span>
              </div>
            </div>

            <ul className="mt-4 grid grid-cols-2 gap-x-4 gap-y-2">
              {chartData.map((entry) => {
                const pct = Math.round((entry.value / total) * 100)
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
          </>
        )}
      </CardContent>
    </Card>
  )
}

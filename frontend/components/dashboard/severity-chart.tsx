"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { DonutChart } from "@/components/ui/donut-chart"
import type { DashboardMetrics } from "@/lib/types"

interface SeverityChartProps {
  data: DashboardMetrics["bySeverity"]
}

export function SeverityChart({ data }: SeverityChartProps) {
  // Tremor DonutChart maps labels to colors automatically if we provide categories.
  // We format the data to match Tremor's expected structure.
  const formattedData = [
    { name: "Crítica", value: data.critical },
    { name: "Alta", value: data.high },
    { name: "Media", value: data.medium },
    { name: "Baja", value: data.low },
  ]

  return (
    <Card className="border-border bg-card">
      <CardHeader>
        <CardTitle className="text-foreground">
          Distribución por Severidad
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="flex h-[280px] items-center justify-center">
          <DonutChart
            data={formattedData}
            category="name"
            value="value"
            colors={["blue", "orange", "amber", "emerald"]}
            valueFormatter={(number: number) =>
              Intl.NumberFormat("us").format(number).toString()
            }
            className="h-44 w-44"
          />
        </div>
      </CardContent>
    </Card>
  )
}

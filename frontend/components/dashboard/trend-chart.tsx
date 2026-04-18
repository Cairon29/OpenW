"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/layout/card"
import { AreaChart } from "@/components/ui/data-display/area-chart"
import type { DashboardMetrics } from "@/lib/types"

interface TrendChartProps {
  data: DashboardMetrics["recentTrend"]
}

export function TrendChart({ data }: TrendChartProps) {
  return (
    <Card className="border-border bg-card">
      <CardHeader>
        <CardTitle className="text-foreground">
          Casos Reportados - Últimos 7 Días
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="h-[280px]">
          <AreaChart
            data={data}
            index="date"
            categories={["count"]}
            colors={["orange"]}
            valueFormatter={(number: number) =>
              Intl.NumberFormat("us").format(number).toString()
            }
            showLegend={false}
            showYAxis={true}
            className="h-full"
          />
        </div>
      </CardContent>
    </Card>
  )
}
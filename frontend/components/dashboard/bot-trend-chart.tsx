"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/layout/card"
import { AreaChart } from "@/components/ui/data-display/area-chart"
import type { BotMetrics } from "@/lib/types"

interface BotTrendChartProps {
  data: BotMetrics["usageOverTime"]
}

export function BotTrendChart({ data }: BotTrendChartProps) {
  // Format data to match "Conversaciones por día" legend
  const formattedData = data.map((d) => ({
    date: d.date,
    "Conversaciones por día": d.count,
  }))

  return (
    <Card className="border-border bg-card shadow-sm">
      <CardHeader className="pb-2">
        <CardTitle className="text-foreground text-[15px] font-semibold">
          Uso a lo largo del Tiempo
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="h-[280px] w-full mt-4">
          <AreaChart
            data={formattedData}
            index="date"
            categories={["Conversaciones por día"]}
            colors={["pink"]}
            valueFormatter={(number: number) =>
              Intl.NumberFormat("us").format(number).toString()
            }
            showLegend={true}
            showYAxis={true}
            className="h-full"
          />
        </div>
      </CardContent>
    </Card>
  )
}
"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { DonutChart } from "@/components/ui/donut-chart"
import type { BotMetrics } from "@/lib/types"

interface BotEffectivenessChartProps {
  data: BotMetrics["effectiveness"]
}

export function BotEffectivenessChart({ data }: BotEffectivenessChartProps) {
  const formattedData = [
    { name: "Con Contexto", value: data.conContexto },
    { name: "Sin Contexto", value: data.sinContexto },
  ]

  return (
    <Card className="border-border bg-card shadow-sm overflow-visible">
      <CardHeader className="pb-2">
        <CardTitle className="text-foreground text-[15px] font-semibold">
          Efectividad de Respuestas
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="flex h-[280px] w-full items-center justify-center mt-4">
          <DonutChart
            data={formattedData}
            category="name"
            value="value"
            colors={["orange", "slate"]}
            valueFormatter={(number: number) =>
              `${number}%`
            }
            className="h-56 w-56"
          />
        </div>
      </CardContent>
    </Card>
  )
}

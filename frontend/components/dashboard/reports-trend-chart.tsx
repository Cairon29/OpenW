"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { AreaChart } from "@/components/ui/area-chart"

interface TrendEntry {
  date: string
  count: number
}

interface ReportsTrendChartProps {
  data: TrendEntry[]
}

export function ReportsTrendChart({ data }: ReportsTrendChartProps) {
  return (
    <Card className="border-border bg-card">
      <CardHeader>
        <CardTitle className="text-foreground">Evolución Temporal de Casos</CardTitle>
      </CardHeader>
      <CardContent>
        {data.length === 0 ? (
          <div className="flex h-[220px] items-center justify-center text-muted-foreground text-sm">
            Sin datos para el período seleccionado
          </div>
        ) : (
          <div className="h-[220px]">
            <AreaChart
              data={data}
              index="date"
              categories={["count"]}
              colors={["orange"]}
              valueFormatter={(n: number) => `${n} casos`}
              showLegend={false}
              showYAxis={true}
              className="h-full"
            />
          </div>
        )}
      </CardContent>
    </Card>
  )
}

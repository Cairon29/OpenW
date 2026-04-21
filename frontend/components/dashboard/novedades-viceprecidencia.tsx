"use client"

import { useEffect, useState, useMemo } from "react"
import {
  Bar,
  BarChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/layout/card"
import {
  getNovedadesPorVicepresidencia,
  getDetalleVicepresidencia,
  type VicepresidenciaCount,
  type VicepresidenciaDetalle
} from "@/lib/api"

const BAR_COLOR = "#6366f1"
const BAR_COLOR_DETAIL = "#8b5cf6"
const MIN_BAR = 0.1

export function NovedadesVicepresidencia() {
  const [data, setData] = useState<VicepresidenciaCount[]>([])
  const [loading, setLoading] = useState(true)
  const [selectedVp, setSelectedVp] = useState<VicepresidenciaDetalle | null>(null)
  const [loadingDetail, setLoadingDetail] = useState(false)

  useEffect(() => {
    getNovedadesPorVicepresidencia()
      .then(setData)
      .catch(console.error)
      .finally(() => setLoading(false))
  }, [])

  const chartData = useMemo(
    () => data.map((d) => ({ ...d, _display: d.total || MIN_BAR })),
    [data]
  )

  const detailChartData = useMemo(
    () =>
      selectedVp?.direcciones.map((d) => ({ ...d, _display: d.total || MIN_BAR })) ?? [],
    [selectedVp]
  )

  function handleBarClick(entry: VicepresidenciaCount) {
    setLoadingDetail(true)
    setSelectedVp(null)
    getDetalleVicepresidencia(entry.id_vicepresidencia)
      .then(setSelectedVp)
      .catch(console.error)
      .finally(() => setLoadingDetail(false))
  }

  return (
    <div className="grid grid-cols-2 gap-6">
      <Card className="border-border bg-card">
        <CardHeader className="pb-2">
          <CardTitle className="text-foreground">
            Novedades por Vicepresidencia
          </CardTitle>
        </CardHeader>
        <CardContent>
          {loading ? (
            <p className="text-sm text-muted-foreground">Cargando...</p>
          ) : data.length === 0 ? (
            <p className="text-sm text-muted-foreground">
              Aún no hay novedades registradas.
            </p>
          ) : (
            <div style={{ height: Math.max(120, chartData.length * 28) }} className="w-full">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart
                  data={chartData}
                  layout="vertical"
                  margin={{ top: 4, right: 24, left: 8, bottom: 0 }}
                  barSize={14}
                >
                  <XAxis
                    type="number"
                    allowDecimals={false}
                    tick={{ fontSize: 11, fill: "hsl(var(--muted-foreground))" }}
                    axisLine={false}
                    tickLine={false}
                  />
                  <YAxis
                    type="category"
                    dataKey="vicepresidencia"
                    width={160}
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
                            {item.payload.vicepresidencia}
                          </span>
                          <span className="ml-2 text-muted-foreground">
                            {item.payload.total} novedades
                          </span>
                        </div>
                      )
                    }}
                  />
                  <Bar
                    dataKey="_display"
                    fill={BAR_COLOR}
                    radius={[0, 4, 4, 0]}
                    className="cursor-pointer"
                    onClick={(_: unknown, index: number) => handleBarClick(data[index])}
                  />
                </BarChart>
              </ResponsiveContainer>
            </div>
          )}
        </CardContent>
      </Card>

      <Card className="border-border bg-card">
        <CardHeader className="pb-2">
          <CardTitle className="text-foreground">
            {selectedVp ? selectedVp.vicepresidencia : "Direcciones"}
          </CardTitle>
        </CardHeader>
        <CardContent>
          {!selectedVp && !loadingDetail && (
            <div className="flex h-full items-center justify-center">
              <p className="text-muted-foreground text-sm">
                Seleccioná una vicepresidencia
              </p>
            </div>
          )}
          {loadingDetail && (
            <p className="text-sm text-muted-foreground">Cargando...</p>
          )}
          {selectedVp && !loadingDetail && (
            detailChartData.length === 0 ? (
              <p className="text-sm text-muted-foreground">
                Sin direcciones registradas.
              </p>
            ) : (
              <div style={{ height: 300 }} className="w-full">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart
                    data={detailChartData}
                    margin={{ top: 4, right: 8, left: 8, bottom: 60 }}
                    barSize={20}
                  >
                    <XAxis
                      dataKey="direccion"
                      tick={{ fontSize: 10, fill: "hsl(var(--muted-foreground))" }}
                      axisLine={false}
                      tickLine={false}
                      angle={-35}
                      textAnchor="end"
                      interval={0}
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
                              {item.payload.direccion}
                            </span>
                            <span className="ml-2 text-muted-foreground">
                              {item.payload.total} novedades
                            </span>
                          </div>
                        )
                      }}
                    />
                    <Bar
                      dataKey="_display"
                      fill={BAR_COLOR_DETAIL}
                      radius={[4, 4, 0, 0]}
                    />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            )
          )}
        </CardContent>
      </Card>
    </div>
  )
}

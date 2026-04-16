"use client"

import { AlertTriangle, CheckCircle, Clock, ShieldAlert } from "lucide-react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/layout/card"
import { cn } from "@/lib/utils"

interface KPIs {
  total: number
  critical: number
  resolved: number
  inProgress: number
  resolutionRate: number
}

interface ReportsKpiCardsProps {
  kpis: KPIs
}

interface KpiCardProps {
  title: string
  value: string | number
  description: string
  icon: React.ElementType
  accent?: boolean
  className?: string
}

function KpiCard({ title, value, description, icon: Icon, accent, className }: KpiCardProps) {
  return (
    <Card
      className={cn(
        "border-border",
        accent
          ? "bg-[#fa8200] text-white dark:bg-card dark:text-foreground"
          : "bg-card text-foreground",
        className
      )}
    >
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle
          className={cn(
            "text-sm font-medium",
            accent ? "text-white/80 dark:text-muted-foreground" : "text-muted-foreground"
          )}
        >
          {title}
        </CardTitle>
        <Icon
          className={cn(
            "h-4 w-4",
            accent ? "text-white/80 dark:text-muted-foreground" : "text-muted-foreground"
          )}
        />
      </CardHeader>
      <CardContent>
        <div
          className={cn(
            "text-2xl font-bold",
            accent ? "text-white dark:text-foreground" : "text-foreground"
          )}
        >
          {value}
        </div>
        <p
          className={cn(
            "text-xs mt-1",
            accent ? "text-white/70 dark:text-muted-foreground" : "text-muted-foreground"
          )}
        >
          {description}
        </p>
      </CardContent>
    </Card>
  )
}

export function ReportsKpiCards({ kpis }: ReportsKpiCardsProps) {
  return (
    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
      <KpiCard
        title="Total de Casos"
        value={kpis.total}
        description="Casos en el período seleccionado"
        icon={AlertTriangle}
        accent
      />
      <KpiCard
        title="Críticos"
        value={kpis.critical}
        description="Con severidad crítica"
        icon={ShieldAlert}
      />
      <KpiCard
        title="Resueltos"
        value={kpis.resolved}
        description={`${kpis.resolutionRate}% tasa de resolución`}
        icon={CheckCircle}
      />
      <KpiCard
        title="En Proceso"
        value={kpis.inProgress}
        description="Pendientes de cierre"
        icon={Clock}
      />
    </div>
  )
}

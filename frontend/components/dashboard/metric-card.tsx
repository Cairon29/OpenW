"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { cn } from "@/lib/utils"
import type { LucideIcon } from "lucide-react"
import { useTheme } from "next-themes"

interface MetricCardProps {
  title: string
  value: string | number
  description?: string
  icon: LucideIcon
  trend?: {
    value: number
    isPositive: boolean
  }
  className?: string
}

export function MetricCard({
  title,
  value,
  description,
  icon: Icon,
  trend,
  className,
}: MetricCardProps) {
  const { theme } = useTheme()
  return (
    <Card className={cn("border-border bg-[#fa8200] text-white dark:bg-card dark:text-foreground", className)}>
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-sm font-medium text-white/80 dark:text-muted-foreground">
          {title}
        </CardTitle>
        <Icon className="h-4 w-4 text-white/80 dark:text-muted-foreground" />
      </CardHeader>
      <CardContent>
        <div className="text-2xl font-bold text-white dark:text-foreground">{value}</div>
        {description && (
          <p className="text-xs text-white/70 dark:text-muted-foreground mt-1">{description}</p>
        )}
        {trend && (
          <p
            className={cn(
              "text-xs mt-1 font-medium",
              theme === "dark" 
                ? (trend.isPositive ? "text-green-500" : "text-red-500")
                : "text-white"
            )}
          >
            {trend.isPositive ? "+" : "-"}
            {Math.abs(trend.value)}% desde ayer
          </p>
        )}
      </CardContent>
    </Card>
  )
}

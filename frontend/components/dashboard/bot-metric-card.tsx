"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { cn } from "@/lib/utils"
import type { LucideIcon } from "lucide-react"

interface BotMetricCardProps {
  title: string
  value: string | number
  description?: string
  icon: LucideIcon
  iconColor?: string
  trend?: {
    value: string
    isPositive: boolean
  }
  className?: string
}

export function BotMetricCard({
  title,
  value,
  description,
  icon: Icon,
  iconColor = "text-muted-foreground",
  trend,
  className,
}: BotMetricCardProps) {
  return (
    <Card className={cn("border border-border bg-card shadow-sm", className)}>
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-sm font-medium text-muted-foreground">
          {title}
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="flex items-center gap-3 mt-1 cursor-default select-none">
          <Icon className={cn("h-7 w-7", iconColor)} />
          <div className="text-3xl font-semibold text-foreground tracking-tight">{value}</div>
        </div>
        
        {trend && (
           <div className="flex items-center gap-1.5 mt-3">
             <span className={cn("text-[11px] leading-none", trend.isPositive ? "text-foreground" : "text-muted-foreground")}>
               {trend.isPositive ? "▲" : "▼"}
             </span>
             <p className="text-xs text-muted-foreground font-medium">
               {trend.value}
             </p>
           </div>
        )}
        {!trend && description && (
           <p className="text-xs text-muted-foreground mt-3 font-medium">
             {description}
           </p>
        )}
      </CardContent>
    </Card>
  )
}

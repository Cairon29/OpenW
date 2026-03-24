import { Badge } from "@/components/ui/badge"
import { cn } from "@/lib/utils"
import type { Severity } from "@/lib/types"

const severityConfig = {
  critical: {
    label: "Crítica",
    className: "bg-severity-critical/20 text-severity-critical border-severity-critical/50",
  },
  high: {
    label: "Alta",
    className: "bg-severity-high/20 text-severity-high border-severity-high/50",
  },
  medium: {
    label: "Media",
    className: "bg-severity-medium/20 text-severity-medium border-severity-medium/50",
  },
  low: {
    label: "Baja",
    className: "bg-severity-low/20 text-severity-low border-severity-low/50",
  },
}

interface SeverityBadgeProps {
  severity: Severity
  className?: string
}

export function SeverityBadge({ severity, className }: SeverityBadgeProps) {
  const config = severityConfig[severity]

  return (
    <Badge
      variant="outline"
      className={cn(config.className, "font-medium", className)}
    >
      {config.label}
    </Badge>
  )
}

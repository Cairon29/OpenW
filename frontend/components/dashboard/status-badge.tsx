import { Badge } from "@/components/ui/badge"
import { cn } from "@/lib/utils"
import type { VulnerabilityCase } from "@/lib/types"

const statusConfig = {
  open: {
    label: "Abierto",
    className: "bg-blue-500/20 text-blue-400 border-blue-500/50",
  },
  in_progress: {
    label: "En Progreso",
    className: "bg-yellow-500/20 text-yellow-400 border-yellow-500/50",
  },
  resolved: {
    label: "Resuelto",
    className: "bg-green-500/20 text-green-400 border-green-500/50",
  },
  closed: {
    label: "Cerrado",
    className: "bg-muted text-muted-foreground border-border",
  },
}

interface StatusBadgeProps {
  status: VulnerabilityCase["status"]
  className?: string
}

export function StatusBadge({ status, className }: StatusBadgeProps) {
  const config = statusConfig[status]

  return (
    <Badge
      variant="outline"
      className={cn(config.className, "font-medium", className)}
    >
      {config.label}
    </Badge>
  )
}

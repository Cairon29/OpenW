"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/layout/card"
import { SeverityBadge } from "./severity-badge"
import { StatusBadge } from "./status-badge"
import type { VulnerabilityCase } from "@/lib/types"
import { formatDistanceToNow } from "date-fns"
import { es } from "date-fns/locale"
import { useEffect, useState } from "react"

interface RecentCasesProps {
  cases: VulnerabilityCase[]
}

function TimeAgo({ date }: { date: Date }) {
  const [timeAgo, setTimeAgo] = useState("")

  useEffect(() => {
    setTimeAgo(formatDistanceToNow(date, { addSuffix: true, locale: es }))
  }, [date])

  return <>{timeAgo}</>
}

export function RecentCases({ cases }: RecentCasesProps) {
  return (
    <Card className="border-border bg-card">
      <CardHeader>
        <CardTitle className="text-foreground">Casos Recientes</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {cases.slice(0, 5).map((caseItem) => (
            <div
              key={caseItem.id}
              className="flex items-center justify-between p-3 rounded-lg bg-secondary/50 hover:bg-secondary transition-colors"
            >
              <div className="flex flex-col gap-1">
                <div className="flex items-center gap-2">
                  <span className="font-mono text-xs text-primary">
                    {caseItem.id}
                  </span>
                  <SeverityBadge severity={caseItem.severity} />
                </div>
                <span className="text-sm font-medium text-foreground">
                  {caseItem.title}
                </span>
                <span className="text-xs text-muted-foreground">
                  Reportado por {caseItem.reportedBy} •{" "}
                  <TimeAgo date={caseItem.reportedAt} />
                </span>
              </div>
              <StatusBadge status={caseItem.status} />
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  )
}
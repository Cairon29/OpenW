"use client"

import { format } from "date-fns"
import { es } from "date-fns/locale"
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"
import { SeverityBadge } from "@/components/dashboard/severity-badge"
import { StatusBadge } from "@/components/dashboard/status-badge"
import type { VulnerabilityCase } from "@/lib/types"

interface ReportsTableProps {
  cases: VulnerabilityCase[]
}

export function ReportsTable({ cases }: ReportsTableProps) {
  if (cases.length === 0) {
    return (
      <div className="rounded-lg border border-border bg-card">
        <div className="flex flex-col items-center justify-center py-16 text-center">
          <p className="text-sm text-muted-foreground">
            No hay casos que coincidan con los filtros aplicados.
          </p>
        </div>
      </div>
    )
  }

  return (
    <div className="rounded-lg border border-border bg-card overflow-hidden">
      <div className="overflow-x-auto">
        <Table>
          <TableHeader>
            <TableRow className="border-border hover:bg-transparent">
              <TableHead className="text-muted-foreground font-medium w-[110px]">ID</TableHead>
              <TableHead className="text-muted-foreground font-medium">Título</TableHead>
              <TableHead className="text-muted-foreground font-medium w-[110px]">Severidad</TableHead>
              <TableHead className="text-muted-foreground font-medium w-[120px]">Estado</TableHead>
              <TableHead className="text-muted-foreground font-medium w-[130px]">Categoría</TableHead>
              <TableHead className="text-muted-foreground font-medium w-[130px]">Reportado por</TableHead>
              <TableHead className="text-muted-foreground font-medium w-[120px]">Fecha</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {cases.map((c) => (
              <TableRow
                key={c.id}
                className="border-border hover:bg-secondary/50 transition-colors"
              >
                <TableCell className="font-mono text-xs text-primary font-medium">
                  {c.id}
                </TableCell>
                <TableCell>
                  <div>
                    <p className="text-sm font-medium text-foreground line-clamp-1">{c.title}</p>
                    {c.description && (
                      <p className="text-xs text-muted-foreground line-clamp-1 mt-0.5">
                        {c.description}
                      </p>
                    )}
                  </div>
                </TableCell>
                <TableCell>
                  <SeverityBadge severity={c.severity} />
                </TableCell>
                <TableCell>
                  <StatusBadge status={c.status} />
                </TableCell>
                <TableCell>
                  <span className="inline-flex items-center rounded-md bg-secondary px-2 py-0.5 text-xs font-medium text-foreground border border-border">
                    {c.category}
                  </span>
                </TableCell>
                <TableCell>
                  <div>
                    <p className="text-sm text-foreground">{c.reportedBy}</p>
                    {c.whatsappNumber && (
                      <p className="text-xs text-muted-foreground">{c.whatsappNumber}</p>
                    )}
                  </div>
                </TableCell>
                <TableCell className="text-sm text-muted-foreground whitespace-nowrap">
                  {format(c.reportedAt, "dd MMM yyyy", { locale: es })}
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>
      <div className="border-t border-border px-4 py-3 flex items-center justify-between">
        <p className="text-xs text-muted-foreground">
          Mostrando <span className="font-medium text-foreground">{cases.length}</span>{" "}
          {cases.length === 1 ? "caso" : "casos"}
        </p>
      </div>
    </div>
  )
}

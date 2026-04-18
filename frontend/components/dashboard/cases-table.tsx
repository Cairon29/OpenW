"use client"

import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/data-display/table"
import { SeverityBadge } from "./severity-badge"
import { StatusBadge } from "./status-badge"
import type { VulnerabilityCase } from "@/lib/types"
import { format } from "date-fns"
import { es } from "date-fns/locale"
import { Button } from "@/components/ui/forms/button"
import { Eye, MoreHorizontal } from "lucide-react"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/overlay/dropdown-menu"

interface CasesTableProps {
  cases: VulnerabilityCase[]
}

export function CasesTable({ cases }: CasesTableProps) {
  return (
    <div className="rounded-lg border border-border bg-card w-full overflow-hidden">
      <div className="overflow-x-auto">
        <Table className="min-w-[700px]">
          <TableHeader>
            <TableRow className="border-border hover:bg-transparent">
              <TableHead className="text-muted-foreground w-[100px] shrink-0">ID</TableHead>
              <TableHead className="text-muted-foreground">Título</TableHead>
              <TableHead className="text-muted-foreground w-[100px]">Severidad</TableHead>
              <TableHead className="text-muted-foreground w-[110px]">Estado</TableHead>
              <TableHead className="text-muted-foreground w-[140px] hidden lg:table-cell">Reportado por</TableHead>
              <TableHead className="text-muted-foreground w-[110px] hidden md:table-cell">Fecha</TableHead>
              <TableHead className="text-muted-foreground w-[120px] hidden xl:table-cell">Categoría</TableHead>
              <TableHead className="text-muted-foreground text-right w-[60px]">Acciones</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {cases.length === 0 && (
              <TableRow>
                <TableCell colSpan={8} className="py-12 text-center text-muted-foreground">
                  No se encontraron casos con los filtros aplicados.
                </TableCell>
              </TableRow>
            )}
            {cases.map((caseItem) => (
              <TableRow
                key={caseItem.id}
                className="border-border hover:bg-secondary/50 transition-colors"
              >
                <TableCell className="font-mono text-sm text-primary whitespace-nowrap">
                  {caseItem.id}
                </TableCell>
                <TableCell className="max-w-[260px]">
                  <div className="flex flex-col">
                    <span className="font-medium text-foreground truncate">
                      {caseItem.title}
                    </span>
                    <span className="text-xs text-muted-foreground line-clamp-1">
                      {caseItem.description}
                    </span>
                  </div>
                </TableCell>
                <TableCell>
                  <SeverityBadge severity={caseItem.severity} />
                </TableCell>
                <TableCell>
                  <StatusBadge status={caseItem.status} />
                </TableCell>
                <TableCell className="hidden lg:table-cell">
                  <div className="flex flex-col">
                    <span className="text-sm text-foreground truncate max-w-[130px]">
                      {caseItem.reportedBy}
                    </span>
                    <span className="text-xs text-muted-foreground">
                      {caseItem.whatsappNumber}
                    </span>
                  </div>
                </TableCell>
                <TableCell className="text-sm text-muted-foreground whitespace-nowrap hidden md:table-cell">
                  {format(caseItem.reportedAt, "dd MMM yyyy", { locale: es })}
                </TableCell>
                <TableCell className="hidden xl:table-cell">
                  <span className="inline-flex items-center rounded-md bg-secondary px-2 py-1 text-xs text-secondary-foreground max-w-[110px] truncate">
                    {caseItem.category}
                  </span>
                </TableCell>
                <TableCell className="text-right">
                  <DropdownMenu>
                    <DropdownMenuTrigger asChild>
                      <Button
                        variant="ghost"
                        size="icon"
                        className="h-8 w-8 text-muted-foreground hover:text-foreground"
                      >
                        <MoreHorizontal className="h-4 w-4" />
                        <span className="sr-only">Abrir menú</span>
                      </Button>
                    </DropdownMenuTrigger>
                    <DropdownMenuContent align="end" className="w-48">
                      <DropdownMenuLabel>Acciones</DropdownMenuLabel>
                      <DropdownMenuSeparator />
                      <DropdownMenuItem>
                        <Eye className="mr-2 h-4 w-4" />
                        Ver detalles
                      </DropdownMenuItem>
                      <DropdownMenuItem>Cambiar estado</DropdownMenuItem>
                      <DropdownMenuItem>Asignar a...</DropdownMenuItem>
                      <DropdownMenuSeparator />
                      <DropdownMenuItem className="text-destructive">
                        Eliminar
                      </DropdownMenuItem>
                    </DropdownMenuContent>
                  </DropdownMenu>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>
    </div>
  )
}
"use client"

import type { DateRange } from "react-day-picker"
import { es } from "date-fns/locale"
import { format } from "date-fns"
import { Input } from "@/components/ui/input"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { Button } from "@/components/ui/button"
import { Calendar as CalendarIcon, Download, FileText, Filter, Search } from "lucide-react"
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover"
import { Calendar } from "@/components/ui/calendar"
import { cn } from "@/lib/utils"

interface ReportsFiltersProps {
  search: string
  onSearchChange: (v: string) => void
  severity: string
  onSeverityChange: (v: string) => void
  status: string
  onStatusChange: (v: string) => void
  category: string
  onCategoryChange: (v: string) => void
  categories: string[]
  dateRange: DateRange | undefined
  onDateRangeChange: (range: DateRange | undefined) => void
  onClearAll: () => void
  onExportCSV: () => void
  onExportPDF: () => void
}

export function ReportsFilters({
  search,
  onSearchChange,
  severity,
  onSeverityChange,
  status,
  onStatusChange,
  category,
  onCategoryChange,
  categories,
  dateRange,
  onDateRangeChange,
  onClearAll,
  onExportCSV,
  onExportPDF,
}: ReportsFiltersProps) {
  const dateLabel = dateRange?.from
    ? dateRange.to
      ? `${format(dateRange.from, "dd MMM", { locale: es })} – ${format(dateRange.to, "dd MMM", { locale: es })}`
      : format(dateRange.from, "dd MMM yyyy", { locale: es })
    : null

  return (
    <div className="flex flex-col gap-4">
      {/* Row 1: Search + date + clear */}
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div className="relative flex-1 max-w-sm">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
          <Input
            value={search}
            onChange={(e) => onSearchChange(e.target.value)}
            placeholder="Buscar por ID o título..."
            className="pl-9 bg-secondary border-border text-foreground placeholder:text-muted-foreground hover:border-primary focus-visible:ring-0 focus-visible:border-primary"
          />
        </div>

        <div className="flex items-center gap-2 flex-wrap">
          {/* Date range picker */}
          <Popover>
            <PopoverTrigger asChild>
              <Button
                variant="outline"
                className={cn(
                  "gap-2 border-border bg-secondary text-foreground hover:border-primary min-w-[160px] justify-start",
                  dateLabel && "border-primary text-foreground"
                )}
              >
                <CalendarIcon className="h-4 w-4 text-muted-foreground" />
                <span className="text-sm">{dateLabel ?? "Rango de fechas"}</span>
              </Button>
            </PopoverTrigger>
            <PopoverContent className="w-auto p-0" align="end">
              <Calendar
                mode="range"
                selected={dateRange}
                onSelect={(range) => onDateRangeChange(range)}
                locale={es}
                numberOfMonths={2}
              />
              {dateRange?.from && (
                <div className="border-t p-2 flex justify-end">
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => onDateRangeChange(undefined)}
                    className="text-xs text-muted-foreground"
                  >
                    Limpiar fecha
                  </Button>
                </div>
              )}
            </PopoverContent>
          </Popover>

          {/* Clear filters */}
          <Button
            variant="outline"
            size="icon"
            className="border-border shrink-0"
            onClick={onClearAll}
            title="Limpiar filtros"
          >
            <Filter className="h-4 w-4" />
          </Button>
        </div>
      </div>

      {/* Row 2: Severity + Status + Category + Export */}
      <div className="flex items-center gap-2 flex-wrap justify-between">
        <div className="flex items-center gap-2 flex-wrap">
          <Select value={severity} onValueChange={onSeverityChange}>
            <SelectTrigger className="w-[130px] bg-secondary border-border text-foreground hover:border-primary data-[state=open]:border-primary">
              <SelectValue placeholder="Severidad" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">Severidad</SelectItem>
              <SelectItem value="critical">Crítica</SelectItem>
              <SelectItem value="high">Alta</SelectItem>
              <SelectItem value="medium">Media</SelectItem>
              <SelectItem value="low">Baja</SelectItem>
            </SelectContent>
          </Select>

          <Select value={status} onValueChange={onStatusChange}>
            <SelectTrigger className="w-[130px] bg-secondary border-border text-foreground hover:border-primary data-[state=open]:border-primary">
              <SelectValue placeholder="Estado" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">Estado</SelectItem>
              <SelectItem value="open">Abierta</SelectItem>
              <SelectItem value="in_progress">En proceso</SelectItem>
              <SelectItem value="resolved">Resuelta</SelectItem>
              <SelectItem value="closed">Descartada</SelectItem>
            </SelectContent>
          </Select>

          <Select value={category} onValueChange={onCategoryChange}>
            <SelectTrigger className="w-[150px] bg-secondary border-border text-foreground hover:border-primary data-[state=open]:border-primary">
              <SelectValue placeholder="Categoría" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">Categoría</SelectItem>
              {categories.map((cat) => (
                <SelectItem key={cat} value={cat}>
                  {cat}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        {/* Export buttons */}
        <div className="flex items-center gap-2">
          <Button
            variant="outline"
            size="sm"
            className="gap-2 border-border text-foreground hover:border-primary"
            onClick={onExportCSV}
          >
            <Download className="h-4 w-4" />
            Excel
          </Button>
          <Button
            size="sm"
            className="gap-2 bg-[#fa8200] hover:bg-[#e07200] text-white"
            onClick={onExportPDF}
          >
            <FileText className="h-4 w-4" />
            PDF
          </Button>
        </div>
      </div>
    </div>
  )
}

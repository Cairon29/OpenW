"use client"

import type { DateRange } from "react-day-picker"
import { es } from "date-fns/locale"
import { Input } from "@/components/ui/forms/input"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/forms/select"
import { Button } from "@/components/ui/forms/button"
import { Calendar as CalendarIcon, Filter, Search } from "lucide-react"
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/overlay/popover"
import { Calendar } from "@/components/ui/forms/calendar"
import { cn } from "@/lib/utils"

interface CasesFiltersProps {
  search: string
  onSearchChange: (v: string) => void
  severity: string
  onSeverityChange: (v: string) => void
  status: string
  onStatusChange: (v: string) => void
  dateRange: DateRange | undefined
  onDateRangeChange: (range: DateRange | undefined) => void
  onClearAll: () => void
}

export function CasesFilters({
  search,
  onSearchChange,
  severity,
  onSeverityChange,
  status,
  onStatusChange,
  dateRange,
  onDateRangeChange,
  onClearAll,
}: CasesFiltersProps) {
  return (
    <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
      <div className="flex flex-1 items-center gap-2">
        <div className="relative flex-1 max-w-sm">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
          <Input
            value={search}
            onChange={(e) => onSearchChange(e.target.value)}
            placeholder="Buscar por ID o título..."
            className="pl-9 bg-secondary border-border text-foreground placeholder:text-muted-foreground hover:border-primary focus-visible:ring-0 focus-visible:border-primary"
          />
        </div>
      </div>

      <div className="flex items-center gap-2">
        <Select value={severity} onValueChange={onSeverityChange}>
          <SelectTrigger className="w-[140px] bg-secondary border-border text-foreground hover:border-primary data-[state=open]:border-primary">
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
          <SelectTrigger className="w-[140px] bg-secondary border-border text-foreground hover:border-primary data-[state=open]:border-primary">
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

        <Popover>
          <PopoverTrigger asChild>
            <Button
              variant="default"
              size="icon"
              className={cn(
                dateRange?.from && "opacity-90",
              )}
            >
              <CalendarIcon className="h-4 w-4" />
            </Button>
          </PopoverTrigger>
          <PopoverContent className="w-auto p-0" align="end">
            <Calendar
              mode="range"
              selected={dateRange}
              onSelect={(range) => onDateRangeChange(range)}
              locale={es}
              numberOfMonths={1}
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

        <Button
          variant="outline"
          size="icon"
          className="border-border"
          onClick={onClearAll}
        >
          <Filter className="h-4 w-4" />
        </Button>
      </div>
    </div>
  )
}
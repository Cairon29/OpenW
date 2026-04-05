"use client"

import { useEffect, useMemo, useState } from "react"
import type { DateRange } from "react-day-picker"
import { startOfDay, endOfDay } from "date-fns"
import { CasesTable } from "@/components/dashboard/cases-table"
import { CasesFilters } from "@/components/dashboard/cases-filters"
import { NewCaseForm } from "@/components/dashboard/new-case-form"
import { Button } from "@/components/ui/button"
import { Plus } from "lucide-react"
import type { VulnerabilityCase } from "@/lib/types"
import { getNovedades } from "@/lib/api"

export default function CasesPage() {
  const [cases, setCases] = useState<VulnerabilityCase[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState("")
  const [modalOpen, setModalOpen] = useState(false)
  const [search, setSearch] = useState("")
  const [severityFilter, setSeverityFilter] = useState("all")
  const [statusFilter, setStatusFilter] = useState("all")
  const [dateRange, setDateRange] = useState<DateRange | undefined>(undefined)

  const loadCases = () => {
    setLoading(true)
    getNovedades()
      .then(setCases)
      .catch(() => setError("No se pudieron cargar los casos"))
      .finally(() => setLoading(false))
  }

  useEffect(() => {
    loadCases()
  }, [])

  const handleCreated = (newCase: VulnerabilityCase) => {
    setCases((prev) => [newCase, ...prev])
  }

  const handleClearAll = () => {
    setSearch("")
    setSeverityFilter("all")
    setStatusFilter("all")
    setDateRange(undefined)
  }

  const filteredCases = useMemo(() => {
    return cases.filter((c) => {
      const q = search.toLowerCase()
      const matchesSearch =
        !q ||
        c.id.toLowerCase().includes(q) ||
        c.title.toLowerCase().includes(q)
      const matchesSeverity =
        severityFilter === "all" || c.severity === severityFilter
      const matchesStatus =
        statusFilter === "all" || c.status === statusFilter
      const matchesDate = (() => {
        if (!dateRange?.from) return true
        const from = startOfDay(dateRange.from)
        const to = endOfDay(dateRange.to ?? dateRange.from)
        return c.reportedAt >= from && c.reportedAt <= to
      })()
      return matchesSearch && matchesSeverity && matchesStatus && matchesDate
    })
  }, [cases, search, severityFilter, statusFilter, dateRange])

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div className="flex flex-col gap-2">
          <h1 className="text-2xl font-bold text-foreground">Casos</h1>
          <p className="text-muted-foreground">
            Gestión de casos de vulnerabilidades reportados
          </p>
        </div>
        <Button className="gap-2" onClick={() => setModalOpen(true)}>
          <Plus className="h-4 w-4" />
          Nuevo Caso
        </Button>
      </div>

      <NewCaseForm
        open={modalOpen}
        onOpenChange={setModalOpen}
        onCreated={handleCreated}
      />

      <CasesFilters
        search={search}
        onSearchChange={setSearch}
        severity={severityFilter}
        onSeverityChange={setSeverityFilter}
        status={statusFilter}
        onStatusChange={setStatusFilter}
        dateRange={dateRange}
        onDateRangeChange={setDateRange}
        onClearAll={handleClearAll}
      />

      {loading && (
        <p className="text-muted-foreground text-sm">Cargando casos...</p>
      )}
      {error && (
        <p className="text-destructive text-sm">{error}</p>
      )}
      {!loading && !error && (
        <>
          <CasesTable cases={filteredCases} />
          <div className="flex items-center justify-between text-sm text-muted-foreground">
            <span>Mostrando {filteredCases.length} de {cases.length} casos</span>
            <div className="flex items-center gap-2">
              <Button variant="outline" size="sm" disabled>Anterior</Button>
              <Button variant="outline" size="sm" disabled>Siguiente</Button>
            </div>
          </div>
        </>
      )}
    </div>
  )
}

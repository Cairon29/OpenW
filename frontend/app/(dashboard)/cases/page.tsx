"use client"

import { useEffect, useState } from "react"
import { CasesTable } from "@/components/dashboard/cases-table"
import { CasesFilters } from "@/components/dashboard/cases-filters"
import { NewCaseForm } from "@/components/dashboard/new-case-form"
import { PageHeader } from "@/components/dashboard/page-header"
import { Button } from "@/components/ui/forms/button"
import { Plus } from "lucide-react"
import type { VulnerabilityCase } from "@/lib/types"
import { getNovedades } from "@/lib/api"
import { useCasesFilter } from "@/hooks/use-cases-filter"

export default function CasesPage() {
  const [cases, setCases] = useState<VulnerabilityCase[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState("")
  const [modalOpen, setModalOpen] = useState(false)

  const {
    search, setSearch,
    severityFilter, setSeverityFilter,
    statusFilter, setStatusFilter,
    dateRange, setDateRange,
    clearAll,
    filteredCases,
  } = useCasesFilter(cases)

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

  return (
    <div className="space-y-6 w-full min-w-0">
      <PageHeader
        title="Casos"
        description="Gestión de casos de vulnerabilidades reportados"
        action={
          <Button className="gap-2" onClick={() => setModalOpen(true)}>
            <Plus className="h-4 w-4" />
            Nuevo Caso
          </Button>
        }
      />

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
        onClearAll={clearAll}
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
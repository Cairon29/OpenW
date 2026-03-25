"use client"

import { useEffect, useState } from "react"
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

      <CasesFilters />

      {loading && (
        <p className="text-muted-foreground text-sm">Cargando casos...</p>
      )}
      {error && (
        <p className="text-destructive text-sm">{error}</p>
      )}
      {!loading && !error && (
        <>
          <CasesTable cases={cases} />
          <div className="flex items-center justify-between text-sm text-muted-foreground">
            <span>Mostrando {cases.length} de {cases.length} casos</span>
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

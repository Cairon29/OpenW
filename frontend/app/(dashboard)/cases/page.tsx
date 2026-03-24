import { CasesTable } from "@/components/dashboard/cases-table"
import { CasesFilters } from "@/components/dashboard/cases-filters"
import { mockCases } from "@/lib/mock-data"
import { Button } from "@/components/ui/button"
import { Plus } from "lucide-react"

export default function CasesPage() {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div className="flex flex-col gap-2">
          <h1 className="text-2xl font-bold text-foreground">Casos</h1>
          <p className="text-muted-foreground">
            Gestión de casos de vulnerabilidades reportados
          </p>
        </div>
        <Button className="gap-2">
          <Plus className="h-4 w-4" />
          Nuevo Caso
        </Button>
      </div>

      <CasesFilters />

      <CasesTable cases={mockCases} />

      <div className="flex items-center justify-between text-sm text-muted-foreground">
        <span>Mostrando {mockCases.length} de {mockCases.length} casos</span>
        <div className="flex items-center gap-2">
          <Button variant="outline" size="sm" disabled>
            Anterior
          </Button>
          <Button variant="outline" size="sm" disabled>
            Siguiente
          </Button>
        </div>
      </div>
    </div>
  )
}

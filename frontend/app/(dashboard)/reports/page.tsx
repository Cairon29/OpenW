"use client"

import { useEffect, useState, useCallback } from "react"
import { format } from "date-fns"
import { es } from "date-fns/locale"
import { BarChart3 } from "lucide-react"
import * as XLSX from "xlsx"
import { getNovedades } from "@/lib/api"
import { useReportsFilter } from "@/hooks/use-reports-filter"
import { PageHeader } from "@/components/dashboard/page-header"
import { ReportsFilters } from "@/components/dashboard/reports-filters"
import { ReportsKpiCards } from "@/components/dashboard/reports-kpi-cards"
import { ReportsSeverityChart } from "@/components/dashboard/reports-severity-chart"
import { ReportsStatusChart } from "@/components/dashboard/reports-status-chart"
import { ReportsTrendChart } from "@/components/dashboard/reports-trend-chart"
import { ReportsTable } from "@/components/dashboard/reports-table"
import type { VulnerabilityCase } from "@/lib/types"

// ── CSV export ────────────────────────────────────────────────────────────────

const SEVERITY_LABELS: Record<string, string> = {
  critical: "Crítica",
  high: "Alta",
  medium: "Media",
  low: "Baja",
}

const STATUS_LABELS: Record<string, string> = {
  open: "Abierta",
  in_progress: "En proceso",
  resolved: "Resuelta",
  closed: "Descartada",
}

function exportToExcel(cases: VulnerabilityCase[]) {
  const headers = ["ID", "Título", "Descripción", "Severidad", "Estado", "Categoría", "Reportado por", "Teléfono", "Fecha"]

  const rows = cases.map((c) => [
    c.id,
    c.title,
    c.description,
    SEVERITY_LABELS[c.severity] ?? c.severity,
    STATUS_LABELS[c.status] ?? c.status,
    c.category,
    c.reportedBy,
    c.whatsappNumber,
    format(c.reportedAt, "dd/MM/yyyy HH:mm", { locale: es }),
  ])

  const wsData = [headers, ...rows]
  const ws = XLSX.utils.aoa_to_sheet(wsData)

  // Ancho de columnas
  ws["!cols"] = [
    { wch: 12 },  // ID
    { wch: 30 },  // Título
    { wch: 55 },  // Descripción
    { wch: 12 },  // Severidad
    { wch: 14 },  // Estado
    { wch: 20 },  // Categoría
    { wch: 22 },  // Reportado por
    { wch: 18 },  // Teléfono
    { wch: 18 },  // Fecha
  ]

  // Estilo de cabecera (fondo naranja, texto blanco, negrita)
  const headerStyle = {
    fill: { fgColor: { rgb: "FA8200" } },
    font: { bold: true, color: { rgb: "FFFFFF" }, sz: 11 },
    alignment: { horizontal: "center", vertical: "center" },
    border: {
      bottom: { style: "thin", color: { rgb: "CCCCCC" } },
    },
  }

  headers.forEach((_, colIdx) => {
    const cellRef = XLSX.utils.encode_cell({ r: 0, c: colIdx })
    if (ws[cellRef]) ws[cellRef].s = headerStyle
  })

  // Estilo filas de datos (alternado y alineación)
  rows.forEach((_, rowIdx) => {
    const isEven = rowIdx % 2 === 0
    headers.forEach((_, colIdx) => {
      const cellRef = XLSX.utils.encode_cell({ r: rowIdx + 1, c: colIdx })
      if (!ws[cellRef]) return
      ws[cellRef].s = {
        fill: { fgColor: { rgb: isEven ? "FFFFFF" : "FFF3E0" } },
        font: { sz: 10 },
        alignment: { vertical: "center", wrapText: colIdx === 2 },
        border: {
          bottom: { style: "hair", color: { rgb: "DDDDDD" } },
          right: { style: "hair", color: { rgb: "DDDDDD" } },
        },
      }
    })
  })

  // Altura de fila de cabecera
  ws["!rows"] = [{ hpt: 22 }]

  const wb = XLSX.utils.book_new()
  XLSX.utils.book_append_sheet(wb, ws, "Vulnerabilidades")

  XLSX.writeFile(wb, `reporte-vulnerabilidades-${format(new Date(), "yyyy-MM-dd")}.xlsx`, {
    bookType: "xlsx",
    cellStyles: true,
  })
}

// ── PDF export ────────────────────────────────────────────────────────────────

function exportToPDF(cases: VulnerabilityCase[], kpis: { total: number; critical: number; resolved: number; resolutionRate: number }) {
  const printWindow = window.open("", "_blank", "width=900,height=700")
  if (!printWindow) return

  const rows = cases
    .map(
      (c) => `
      <tr>
        <td style="font-family:monospace;font-size:12px;color:#fa8200">${c.id}</td>
        <td>${c.title}</td>
        <td>${SEVERITY_LABELS[c.severity] ?? c.severity}</td>
        <td>${STATUS_LABELS[c.status] ?? c.status}</td>
        <td>${c.category}</td>
        <td>${c.reportedBy}</td>
        <td>${format(c.reportedAt, "dd/MM/yyyy", { locale: es })}</td>
      </tr>`
    )
    .join("")

  const html = `<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8" />
  <title>Reporte de Vulnerabilidades</title>
  <style>
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body { font-family: Arial, Helvetica, sans-serif; font-size: 13px; color: #111; padding: 32px; }
    .header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 24px; border-bottom: 2px solid #fa8200; padding-bottom: 16px; }
    .brand { font-size: 22px; font-weight: bold; color: #111; }
    .brand span { color: #fa8200; }
    .meta { text-align: right; font-size: 11px; color: #555; }
    .kpis { display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; margin-bottom: 24px; }
    .kpi { border: 1px solid #e5e7eb; border-radius: 8px; padding: 12px; text-align: center; }
    .kpi-value { font-size: 28px; font-weight: bold; color: #fa8200; }
    .kpi-label { font-size: 11px; color: #6b7280; margin-top: 4px; }
    .section-title { font-size: 14px; font-weight: 600; margin-bottom: 10px; color: #111; }
    table { width: 100%; border-collapse: collapse; margin-bottom: 24px; }
    th { background: #f9fafb; text-align: left; padding: 8px 10px; font-size: 11px; font-weight: 600; color: #374151; border-bottom: 1px solid #e5e7eb; border-top: 1px solid #e5e7eb; }
    td { padding: 7px 10px; font-size: 12px; border-bottom: 1px solid #f3f4f6; vertical-align: top; }
    tr:last-child td { border-bottom: none; }
    .footer { text-align: center; font-size: 10px; color: #9ca3af; margin-top: 32px; padding-top: 16px; border-top: 1px solid #e5e7eb; }
    @media print { body { padding: 16px; } }
  </style>
</head>
<body>
  <div class="header">
    <div>
      <div class="brand"><span>{</span>fiduprevisora<span>)</span></div>
      <div style="font-size:11px;color:#9ca3af;margin-top:4px;letter-spacing:0.1em">SECURITY DASHBOARD</div>
    </div>
    <div class="meta">
      <div style="font-size:15px;font-weight:600;color:#111;margin-bottom:4px">Reporte de Vulnerabilidades</div>
      <div>Generado: ${format(new Date(), "dd 'de' MMMM 'de' yyyy, HH:mm", { locale: es })}</div>
      <div>${cases.length} caso${cases.length !== 1 ? "s" : ""} exportado${cases.length !== 1 ? "s" : ""}</div>
    </div>
  </div>

  <div class="kpis">
    <div class="kpi">
      <div class="kpi-value">${kpis.total}</div>
      <div class="kpi-label">Total de casos</div>
    </div>
    <div class="kpi">
      <div class="kpi-value" style="color:#ef4444">${kpis.critical}</div>
      <div class="kpi-label">Críticos</div>
    </div>
    <div class="kpi">
      <div class="kpi-value" style="color:#10b981">${kpis.resolved}</div>
      <div class="kpi-label">Resueltos</div>
    </div>
    <div class="kpi">
      <div class="kpi-value">${kpis.resolutionRate}%</div>
      <div class="kpi-label">Tasa de resolución</div>
    </div>
  </div>

  <div class="section-title">Detalle de casos</div>
  <table>
    <thead>
      <tr>
        <th>ID</th>
        <th>Título</th>
        <th>Severidad</th>
        <th>Estado</th>
        <th>Categoría</th>
        <th>Reportado por</th>
        <th>Fecha</th>
      </tr>
    </thead>
    <tbody>${rows}</tbody>
  </table>

  <div class="footer">
    Reporte generado automáticamente por Fiduprevisora Security Dashboard &nbsp;·&nbsp; ${new Date().getFullYear()}
  </div>

  <script>window.onload = () => { window.print(); window.onafterprint = () => window.close(); }<\/script>
</body>
</html>`

  printWindow.document.open()
  printWindow.document.write(html)
  printWindow.document.close()
}

// ── Page ──────────────────────────────────────────────────────────────────────

export default function ReportsPage() {
  const [allCases, setAllCases] = useState<VulnerabilityCase[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    getNovedades()
      .then(setAllCases)
      .catch(console.error)
      .finally(() => setLoading(false))
  }, [])

  const {
    search, setSearch,
    severityFilter, setSeverityFilter,
    statusFilter, setStatusFilter,
    categoryFilter, setCategoryFilter,
    dateRange, setDateRange,
    clearAll,
    filteredCases,
    kpis,
    severityData,
    statusData,
    trendData,
    categories,
  } = useReportsFilter(allCases)

  const handleExportCSV = useCallback(() => exportToExcel(filteredCases), [filteredCases])
  const handleExportPDF = useCallback(() => exportToPDF(filteredCases, kpis), [filteredCases, kpis])

  return (
    <div className="space-y-6">
      <PageHeader
        title="Reportes"
        description="Análisis y exportación de vulnerabilidades del sistema"
        action={
          <div className="flex items-center gap-2 text-muted-foreground text-sm">
            <BarChart3 className="h-4 w-4" />
            <span>
              {loading ? "Cargando..." : `${allCases.length} casos en total`}
            </span>
          </div>
        }
      />

      {/* Filters */}
      <div className="rounded-lg border border-border bg-card p-4">
        <ReportsFilters
          search={search}
          onSearchChange={setSearch}
          severity={severityFilter}
          onSeverityChange={setSeverityFilter}
          status={statusFilter}
          onStatusChange={setStatusFilter}
          category={categoryFilter}
          onCategoryChange={setCategoryFilter}
          categories={categories}
          dateRange={dateRange}
          onDateRangeChange={setDateRange}
          onClearAll={clearAll}
          onExportCSV={handleExportCSV}
          onExportPDF={handleExportPDF}
        />
      </div>

      {/* KPI cards */}
      <ReportsKpiCards kpis={kpis} />

      {/* Charts */}
      <div className="grid gap-6 lg:grid-cols-2">
        <ReportsSeverityChart data={severityData} />
        <ReportsStatusChart data={statusData} />
      </div>

      {/* Trend */}
      <ReportsTrendChart data={trendData} />

      {/* Table */}
      <div>
        <h2 className="text-base font-semibold text-foreground mb-3">
          Detalle de casos
          <span className="ml-2 text-sm font-normal text-muted-foreground">
            ({filteredCases.length} resultado{filteredCases.length !== 1 ? "s" : ""})
          </span>
        </h2>
        <ReportsTable cases={filteredCases} />
      </div>
    </div>
  )
}

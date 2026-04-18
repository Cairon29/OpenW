import { useMemo, useState } from "react"
import type { DateRange } from "react-day-picker"
import { startOfDay, endOfDay } from "date-fns"
import type { VulnerabilityCase } from "@/lib/types"

export function useCasesFilter(cases: VulnerabilityCase[]) {
  const [search, setSearch] = useState("")
  const [severityFilter, setSeverityFilter] = useState("all")
  const [statusFilter, setStatusFilter] = useState("all")
  const [dateRange, setDateRange] = useState<DateRange | undefined>(undefined)

  const clearAll = () => {
    setSearch("")
    setSeverityFilter("all")
    setStatusFilter("all")
    setDateRange(undefined)
  }

  const filteredCases = useMemo(
    () =>
      cases.filter((c) => {
        const q = search.toLowerCase()
        const matchesSearch =
          !q || c.id.toLowerCase().includes(q) || c.title.toLowerCase().includes(q)
        const matchesSeverity = severityFilter === "all" || c.severity === severityFilter
        const matchesStatus = statusFilter === "all" || c.status === statusFilter
        const matchesDate = (() => {
          if (!dateRange?.from) return true
          const from = startOfDay(dateRange.from)
          const to = endOfDay(dateRange.to ?? dateRange.from)
          return c.reportedAt >= from && c.reportedAt <= to
        })()
        return matchesSearch && matchesSeverity && matchesStatus && matchesDate
      }),
    [cases, search, severityFilter, statusFilter, dateRange]
  )

  return {
    search,
    setSearch,
    severityFilter,
    setSeverityFilter,
    statusFilter,
    setStatusFilter,
    dateRange,
    setDateRange,
    clearAll,
    filteredCases,
  }
}

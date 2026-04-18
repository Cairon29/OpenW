import { useMemo, useState } from "react"
import type { DateRange } from "react-day-picker"
import { startOfDay, endOfDay, format } from "date-fns"
import { es } from "date-fns/locale"
import type { VulnerabilityCase } from "@/lib/types"

export function useReportsFilter(cases: VulnerabilityCase[]) {
  const [search, setSearch] = useState("")
  const [severityFilter, setSeverityFilter] = useState("all")
  const [statusFilter, setStatusFilter] = useState("all")
  const [categoryFilter, setCategoryFilter] = useState("all")
  const [dateRange, setDateRange] = useState<DateRange | undefined>(undefined)

  const clearAll = () => {
    setSearch("")
    setSeverityFilter("all")
    setStatusFilter("all")
    setCategoryFilter("all")
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
        const matchesCategory = categoryFilter === "all" || c.category === categoryFilter
        const matchesDate = (() => {
          if (!dateRange?.from) return true
          const from = startOfDay(dateRange.from)
          const to = endOfDay(dateRange.to ?? dateRange.from)
          return c.reportedAt >= from && c.reportedAt <= to
        })()
        return matchesSearch && matchesSeverity && matchesStatus && matchesCategory && matchesDate
      }),
    [cases, search, severityFilter, statusFilter, categoryFilter, dateRange]
  )

  const kpis = useMemo(() => {
    const total = filteredCases.length
    const critical = filteredCases.filter((c) => c.severity === "critical").length
    const resolved = filteredCases.filter((c) => c.status === "resolved" || c.status === "closed").length
    const inProgress = filteredCases.filter((c) => c.status === "in_progress").length
    const resolutionRate = total > 0 ? Math.round((resolved / total) * 100) : 0
    return { total, critical, resolved, inProgress, resolutionRate }
  }, [filteredCases])

  const severityData = useMemo(() => {
    const counts = { critical: 0, high: 0, medium: 0, low: 0 }
    filteredCases.forEach((c) => {
      if (c.severity in counts) counts[c.severity as keyof typeof counts]++
    })
    return counts
  }, [filteredCases])

  const statusData = useMemo(() => {
    const counts = { open: 0, in_progress: 0, resolved: 0, closed: 0 }
    filteredCases.forEach((c) => {
      if (c.status in counts) counts[c.status as keyof typeof counts]++
    })
    return counts
  }, [filteredCases])

  const trendData = useMemo(() => {
    const counts: Record<string, { display: string; count: number }> = {}
    filteredCases.forEach((c) => {
      const key = format(c.reportedAt, "yyyy-MM-dd")
      if (!counts[key]) {
        counts[key] = {
          display: format(c.reportedAt, "dd MMM", { locale: es }),
          count: 0,
        }
      }
      counts[key].count++
    })
    return Object.entries(counts)
      .sort((a, b) => a[0].localeCompare(b[0]))
      .map(([, { display, count }]) => ({ date: display, count }))
  }, [filteredCases])

  const categories = useMemo(() => {
    const seen = new Set<string>()
    cases.forEach((c) => seen.add(c.category))
    return Array.from(seen).sort()
  }, [cases])

  return {
    search,
    setSearch,
    severityFilter,
    setSeverityFilter,
    statusFilter,
    setStatusFilter,
    categoryFilter,
    setCategoryFilter,
    dateRange,
    setDateRange,
    clearAll,
    filteredCases,
    kpis,
    severityData,
    statusData,
    trendData,
    categories,
  }
}

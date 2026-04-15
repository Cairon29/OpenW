"use client"

import { useState } from "react"
import { Loader2, CheckCircle2, XCircle, Plug } from "lucide-react"
import { Button } from "@/components/ui/button"
import { testConnection } from "@/lib/api"
import type { ConnectionTestResult } from "@/lib/types"

interface ConnectionCardProps {
  service: string
  label: string
  description: string
  icon: React.ReactNode
}

export function ConnectionCard({ service, label, description, icon }: ConnectionCardProps) {
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<ConnectionTestResult | null>(null)

  async function handleTest() {
    setLoading(true)
    setResult(null)
    try {
      const r = await testConnection(service)
      setResult(r)
    } catch {
      setResult({ service, ok: false, message: "Error al contactar el servidor." })
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="rounded-lg border border-border p-4 space-y-3">
      <div className="flex items-start justify-between gap-3">
        <div className="flex items-start gap-3">
          <div className="mt-0.5 text-[#fa8200]">{icon}</div>
          <div>
            <p className="text-sm font-semibold">{label}</p>
            <p className="text-xs text-muted-foreground leading-relaxed mt-0.5">{description}</p>
          </div>
        </div>
        <Button
          variant="outline"
          size="sm"
          className="shrink-0 gap-1.5 text-xs"
          onClick={handleTest}
          disabled={loading}
        >
          {loading ? (
            <Loader2 className="h-3.5 w-3.5 animate-spin" />
          ) : (
            <Plug className="h-3.5 w-3.5" />
          )}
          Probar
        </Button>
      </div>

      {result && (
        <div
          className={`flex items-start gap-2 rounded-md px-3 py-2 text-xs ${
            result.ok
              ? "bg-green-500/10 text-green-700 dark:text-green-400"
              : "bg-destructive/10 text-destructive"
          }`}
        >
          {result.ok ? (
            <CheckCircle2 className="h-3.5 w-3.5 mt-0.5 shrink-0" />
          ) : (
            <XCircle className="h-3.5 w-3.5 mt-0.5 shrink-0" />
          )}
          <span>{result.message}</span>
        </div>
      )}
    </div>
  )
}

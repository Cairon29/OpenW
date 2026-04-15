"use client"

import { useState, useEffect } from "react"
import { Eye, EyeOff, Loader2, Check, X, AlertCircle } from "lucide-react"
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"
import { Switch } from "@/components/ui/switch"
import { Textarea } from "@/components/ui/textarea"
import { Label } from "@/components/ui/label"
import type { SystemConfig } from "@/lib/types"
import { updateConfiguration } from "@/lib/api"

interface SettingsFieldProps {
  config: SystemConfig
  onSaved?: (updated: SystemConfig) => void
}

export function SettingsField({ config, onSaved }: SettingsFieldProps) {
  // Sensitive fields always start empty so the user types the full new value.
  // Non-sensitive fields start with the current stored value.
  const [value, setValue] = useState(() =>
    config.is_sensitive ? "" : (config.value ?? "")
  )
  const [showSecret, setShowSecret] = useState(false)
  const [saving, setSaving] = useState(false)
  const [saved, setSaved] = useState(false)
  const [error, setError] = useState<string | null>(null)

  // Keep non-sensitive fields in sync if the parent refreshes configs.
  useEffect(() => {
    if (!config.is_sensitive) {
      setValue(config.value ?? "")
    }
  }, [config.value, config.is_sensitive])

  // Dirty: for sensitive fields, any non-empty input is a change.
  const isDirty = config.is_sensitive
    ? value.trim() !== ""
    : value !== (config.value ?? "")

  // ── Save helpers ──────────────────────────────────────────────────────────

  async function save() {
    setSaving(true)
    setError(null)
    try {
      const updated = await updateConfiguration(config.key, value)
      setSaved(true)
      setTimeout(() => setSaved(false), 2500)
      // After saving a sensitive field, clear it so the field shows the placeholder again.
      if (config.is_sensitive) setValue("")
      onSaved?.(updated)
    } catch {
      setError("No se pudo guardar. Verifica la conexión con el servidor.")
    } finally {
      setSaving(false)
    }
  }

  function cancel() {
    if (config.is_sensitive) {
      setValue("")
    } else {
      setValue(config.value ?? "")
    }
    setError(null)
  }

  async function handleToggle(checked: boolean) {
    setSaving(true)
    setError(null)
    try {
      const updated = await updateConfiguration(config.key, checked ? "true" : "false")
      setValue(checked ? "true" : "false")
      setSaved(true)
      setTimeout(() => setSaved(false), 2500)
      onSaved?.(updated)
    } catch {
      setError("No se pudo guardar.")
    } finally {
      setSaving(false)
    }
  }

  // ── Boolean field ──────────────────────────────────────────────────────────
  if (config.value_type === "boolean") {
    const isOn = value === "true" || value === "1"
    return (
      <div className="flex items-start justify-between gap-4 py-3.5 border-b border-border/40 last:border-0">
        <div className="flex-1 min-w-0">
          <Label className="text-sm font-medium">{config.label}</Label>
          {config.description && (
            <p className="text-xs text-muted-foreground mt-0.5 leading-relaxed">{config.description}</p>
          )}
          {error && (
            <p className="text-xs text-destructive mt-1 flex items-center gap-1">
              <AlertCircle className="h-3 w-3" />{error}
            </p>
          )}
        </div>
        <div className="flex items-center gap-2 shrink-0">
          {saving && <Loader2 className="h-3.5 w-3.5 animate-spin text-muted-foreground" />}
          {saved && !saving && <Check className="h-3.5 w-3.5 text-green-500" />}
          <Switch
            checked={isOn}
            onCheckedChange={handleToggle}
            disabled={saving}
            className="data-[state=checked]:bg-[#fa8200]"
          />
        </div>
      </div>
    )
  }

  // ── JSON field ─────────────────────────────────────────────────────────────
  if (config.value_type === "json") {
    function handleJsonSave() {
      // Validate JSON before saving
      try {
        JSON.parse(value)
      } catch {
        setError("JSON inválido. Ejemplo: [\"palabra1\", \"palabra2\"]")
        return
      }
      save()
    }

    return (
      <div className="py-3.5 border-b border-border/40 last:border-0 space-y-2">
        <Label className="text-sm font-medium">{config.label}</Label>
        {config.description && (
          <p className="text-xs text-muted-foreground leading-relaxed">{config.description}</p>
        )}
        <Textarea
          value={value}
          onChange={(e) => { setValue(e.target.value); setError(null) }}
          rows={3}
          className="font-mono text-xs resize-none"
          placeholder='["palabra1", "palabra2"]'
        />
        {error && (
          <p className="text-xs text-destructive flex items-center gap-1">
            <AlertCircle className="h-3 w-3 shrink-0" />{error}
          </p>
        )}
        {saved && !isDirty && (
          <p className="text-xs text-green-600 dark:text-green-400 flex items-center gap-1">
            <Check className="h-3 w-3" /> Guardado
          </p>
        )}
        {isDirty && (
          <div className="flex justify-end gap-2">
            <Button variant="ghost" size="sm" onClick={cancel} disabled={saving}>
              <X className="h-3.5 w-3.5 mr-1" /> Cancelar
            </Button>
            <Button
              size="sm"
              className="bg-[#fa8200] hover:bg-[#e07200] text-white"
              onClick={handleJsonSave}
              disabled={saving}
            >
              {saving
                ? <Loader2 className="h-3.5 w-3.5 animate-spin mr-1" />
                : <Check className="h-3.5 w-3.5 mr-1" />}
              Guardar
            </Button>
          </div>
        )}
      </div>
    )
  }

  // ── String / Number field ──────────────────────────────────────────────────
  const inputType = config.is_sensitive && !showSecret ? "password" : "text"

  // Hint shown below sensitive fields to indicate the current stored value is masked.
  const hasMaskedValue = config.is_sensitive && config.value && config.value.trim() !== ""

  return (
    <div className="py-3.5 border-b border-border/40 last:border-0 space-y-1.5">
      <Label className="text-sm font-medium">{config.label}</Label>
      {config.description && (
        <p className="text-xs text-muted-foreground leading-relaxed">{config.description}</p>
      )}
      {hasMaskedValue && !isDirty && (
        <p className="text-xs text-muted-foreground/70 italic">
          Valor actual configurado · escribe para reemplazarlo
        </p>
      )}
      <div className="flex gap-2">
        <div className="relative flex-1">
          <Input
            type={inputType}
            value={value}
            onChange={(e) => { setValue(e.target.value); setError(null) }}
            className="text-sm pr-8"
            placeholder={
              config.is_sensitive && hasMaskedValue
                ? config.value ?? "••••••••"  // show masked value as placeholder
                : config.label
            }
          />
          {config.is_sensitive && (
            <button
              type="button"
              className="absolute right-2 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground transition-colors"
              onClick={() => setShowSecret((v) => !v)}
            >
              {showSecret ? <EyeOff className="h-3.5 w-3.5" /> : <Eye className="h-3.5 w-3.5" />}
            </button>
          )}
        </div>

        {isDirty && (
          <>
            <Button
              variant="ghost"
              size="icon"
              className="shrink-0"
              onClick={cancel}
              disabled={saving}
              title="Cancelar"
            >
              <X className="h-3.5 w-3.5" />
            </Button>
            <Button
              size="sm"
              className="shrink-0 bg-[#fa8200] hover:bg-[#e07200] text-white"
              onClick={save}
              disabled={saving}
            >
              {saving
                ? <Loader2 className="h-3.5 w-3.5 animate-spin" />
                : <><Check className="h-3.5 w-3.5 mr-1" />Guardar</>}
            </Button>
          </>
        )}

        {saved && !isDirty && (
          <span className="flex items-center gap-1 text-xs text-green-600 dark:text-green-400 self-center whitespace-nowrap">
            <Check className="h-3.5 w-3.5" /> Guardado
          </span>
        )}
      </div>

      {error && (
        <p className="text-xs text-destructive flex items-center gap-1">
          <AlertCircle className="h-3 w-3 shrink-0" />{error}
        </p>
      )}
    </div>
  )
}

"use client"

import { useEffect, useState } from "react"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Textarea } from "@/components/ui/textarea"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { FieldGroup, Field, FieldLabel } from "@/components/ui/field"
import { createNovedad, getCategorias } from "@/lib/api"
import type { Category, VulnerabilityCase } from "@/lib/types"

interface NewCaseFormProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  onCreated?: (newCase: VulnerabilityCase) => void
}

const severityOptions = [
  { value: "critica", label: "Crítica" },
  { value: "alta", label: "Alta" },
  { value: "media", label: "Media" },
  { value: "baja", label: "Baja" },
  { value: "informativa", label: "Informativa" },
]

const estadoOptions = [
  { value: "abierta", label: "Abierta" },
  { value: "en_proceso", label: "En proceso" },
  { value: "resuelta", label: "Resuelta" },
  { value: "descartada", label: "Descartada" },
]

export function NewCaseForm({ open, onOpenChange, onCreated }: NewCaseFormProps) {
  const [titulo, setTitulo] = useState("")
  const [descripcion, setDescripcion] = useState("")
  const [severidad, setSeveridad] = useState("media")
  const [estado, setEstado] = useState("abierta")
  const [categoriaId, setCategoriaId] = useState<string>("")
  const [userPhone, setUserPhone] = useState("")
  const [categorias, setCategorias] = useState<Category[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState("")

  useEffect(() => {
    if (open) {
      getCategorias().then(setCategorias).catch(() => setCategorias([]))
    }
  }, [open])

  const resetForm = () => {
    setTitulo("")
    setDescripcion("")
    setSeveridad("media")
    setEstado("abierta")
    setCategoriaId("")
    setUserPhone("")
    setError("")
  }

  const handleSubmit = async () => {
    if (!titulo.trim() || !descripcion.trim()) return
    setLoading(true)
    setError("")
    try {
      const created = await createNovedad({
        titulo: titulo.trim(),
        descripcion: descripcion.trim(),
        severidad,
        estado,
        categoria_id: categoriaId ? Number(categoriaId) : null,
        user_phone: userPhone ? Number(userPhone) : null,
      })
      onCreated?.(created)
      resetForm()
      onOpenChange(false)
    } catch {
      setError("No se pudo crear el caso. Intenta de nuevo.")
    } finally {
      setLoading(false)
    }
  }

  const handleClose = (val: boolean) => {
    if (!val) resetForm()
    onOpenChange(val)
  }

  const canSubmit = titulo.trim().length >= 3 && descripcion.trim().length > 0

  return (
    <Dialog open={open} onOpenChange={handleClose}>
      <DialogContent className="sm:max-w-[520px] bg-card border-border">
        <DialogHeader>
          <DialogTitle className="text-foreground">Nuevo Caso</DialogTitle>
          <DialogDescription className="text-muted-foreground">
            Registra manualmente un caso de vulnerabilidad en el sistema.
          </DialogDescription>
        </DialogHeader>

        <FieldGroup className="gap-4">
          <Field>
            <FieldLabel className="text-foreground">
              Título <span className="text-destructive">*</span>
            </FieldLabel>
            <Input
              placeholder="Ej: SQL Injection en formulario de login"
              value={titulo}
              onChange={(e) => setTitulo(e.target.value)}
              className="bg-secondary border-border text-foreground"
            />
          </Field>

          <Field>
            <FieldLabel className="text-foreground">
              Descripción <span className="text-destructive">*</span>
            </FieldLabel>
            <Textarea
              placeholder="Describe el problema o vulnerabilidad detectada..."
              value={descripcion}
              onChange={(e) => setDescripcion(e.target.value)}
              className="bg-secondary border-border text-foreground min-h-[90px]"
            />
          </Field>

          <div className="grid grid-cols-2 gap-4">
            <Field>
              <FieldLabel className="text-foreground">Severidad</FieldLabel>
              <Select value={severidad} onValueChange={setSeveridad}>
                <SelectTrigger className="bg-secondary border-border text-foreground">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent className="bg-card border-border">
                  {severityOptions.map((opt) => (
                    <SelectItem key={opt.value} value={opt.value}>
                      {opt.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </Field>

            <Field>
              <FieldLabel className="text-foreground">Estado</FieldLabel>
              <Select value={estado} onValueChange={setEstado}>
                <SelectTrigger className="bg-secondary border-border text-foreground">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent className="bg-card border-border">
                  {estadoOptions.map((opt) => (
                    <SelectItem key={opt.value} value={opt.value}>
                      {opt.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </Field>
          </div>

          <Field>
            <FieldLabel className="text-foreground">Categoría</FieldLabel>
            <Select
              value={categoriaId}
              onValueChange={setCategoriaId}
            >
              <SelectTrigger className="bg-secondary border-border text-foreground">
                <SelectValue placeholder="Sin categoría" />
              </SelectTrigger>
              <SelectContent className="bg-card border-border">
                {categorias.map((cat) => (
                  <SelectItem key={cat.id} value={cat.id}>
                    {cat.name}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </Field>

          <Field>
            <FieldLabel className="text-foreground">Teléfono del reportante</FieldLabel>
            <Input
              placeholder="Ej: 573001234567"
              value={userPhone}
              onChange={(e) => setUserPhone(e.target.value.replace(/\D/g, ""))}
              className="bg-secondary border-border text-foreground"
              type="tel"
            />
          </Field>

          {error && (
            <p className="text-destructive text-sm">{error}</p>
          )}
        </FieldGroup>

        <DialogFooter>
          <Button variant="outline" onClick={() => handleClose(false)} disabled={loading}>
            Cancelar
          </Button>
          <Button onClick={handleSubmit} disabled={!canSubmit || loading}>
            {loading ? "Creando..." : "Crear Caso"}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}

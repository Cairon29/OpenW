"use client"

import { useState } from "react"
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
import { Badge } from "@/components/ui/badge"
import { X, Plus } from "lucide-react"
import { FieldGroup, Field, FieldLabel } from "@/components/ui/field"

interface CategoryFormProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  onSubmit?: (data: {
    name: string
    description: string
    keywords: string[]
    color: string
  }) => void
}

const colorOptions = [
  "#ef4444",
  "#f97316",
  "#eab308",
  "#22c55e",
  "#3b82f6",
  "#8b5cf6",
  "#ec4899",
  "#06b6d4",
]

export function CategoryForm({ open, onOpenChange, onSubmit }: CategoryFormProps) {
  const [name, setName] = useState("")
  const [description, setDescription] = useState("")
  const [keywords, setKeywords] = useState<string[]>([])
  const [keywordInput, setKeywordInput] = useState("")
  const [selectedColor, setSelectedColor] = useState(colorOptions[0])

  const handleAddKeyword = () => {
    if (keywordInput.trim() && !keywords.includes(keywordInput.trim())) {
      setKeywords([...keywords, keywordInput.trim()])
      setKeywordInput("")
    }
  }

  const handleRemoveKeyword = (keyword: string) => {
    setKeywords(keywords.filter((k) => k !== keyword))
  }

  const handleSubmit = () => {
    if (name.trim()) {
      onSubmit?.({
        name: name.trim(),
        description: description.trim(),
        keywords,
        color: selectedColor,
      })
      setName("")
      setDescription("")
      setKeywords([])
      setKeywordInput("")
      onOpenChange(false)
    }
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[500px] bg-card border-border">
        <DialogHeader>
          <DialogTitle className="text-foreground">Nueva Categoría</DialogTitle>
          <DialogDescription className="text-muted-foreground">
            Crea una nueva categoría para clasificar vulnerabilidades automáticamente.
          </DialogDescription>
        </DialogHeader>

        <FieldGroup className="gap-4">
          <Field>
            <FieldLabel className="text-foreground">Nombre</FieldLabel>
            <Input
              placeholder="Ej: Inyección SQL"
              value={name}
              onChange={(e) => setName(e.target.value)}
              className="bg-secondary border-border text-foreground"
            />
          </Field>

          <Field>
            <FieldLabel className="text-foreground">Descripción</FieldLabel>
            <Textarea
              placeholder="Describe el tipo de vulnerabilidades que incluye esta categoría..."
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              className="bg-secondary border-border text-foreground min-h-[80px]"
            />
          </Field>

          <Field>
            <FieldLabel className="text-foreground">Color</FieldLabel>
            <div className="flex gap-2">
              {colorOptions.map((color) => (
                <button
                  key={color}
                  type="button"
                  className={`h-8 w-8 rounded-full transition-transform ${
                    selectedColor === color
                      ? "ring-2 ring-primary ring-offset-2 ring-offset-background scale-110"
                      : "hover:scale-110"
                  }`}
                  style={{ backgroundColor: color }}
                  onClick={() => setSelectedColor(color)}
                />
              ))}
            </div>
          </Field>

          <Field>
            <FieldLabel className="text-foreground">Palabras Clave</FieldLabel>
            <div className="flex gap-2">
              <Input
                placeholder="Agregar palabra clave..."
                value={keywordInput}
                onChange={(e) => setKeywordInput(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === "Enter") {
                    e.preventDefault()
                    handleAddKeyword()
                  }
                }}
                className="bg-secondary border-border text-foreground"
              />
              <Button
                type="button"
                variant="secondary"
                size="icon"
                onClick={handleAddKeyword}
              >
                <Plus className="h-4 w-4" />
              </Button>
            </div>
            {keywords.length > 0 && (
              <div className="flex flex-wrap gap-2 mt-2">
                {keywords.map((keyword) => (
                  <Badge
                    key={keyword}
                    variant="secondary"
                    className="bg-secondary text-secondary-foreground gap-1"
                  >
                    {keyword}
                    <button
                      type="button"
                      onClick={() => handleRemoveKeyword(keyword)}
                      className="ml-1 hover:text-destructive"
                    >
                      <X className="h-3 w-3" />
                    </button>
                  </Badge>
                ))}
              </div>
            )}
          </Field>
        </FieldGroup>

        <DialogFooter>
          <Button variant="outline" onClick={() => onOpenChange(false)}>
            Cancelar
          </Button>
          <Button onClick={handleSubmit} disabled={!name.trim()}>
            Crear Categoría
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}

"use client"

import { useState } from "react"
import { CategoryCard } from "@/components/dashboard/category-card"
import { CategoryForm } from "@/components/dashboard/category-form"
import { mockCategories } from "@/lib/mock-data"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Plus, Search } from "lucide-react"
import type { Category } from "@/lib/types"

export default function CategoriesPage() {
  const [categories, setCategories] = useState<Category[]>(mockCategories)
  const [isFormOpen, setIsFormOpen] = useState(false)
  const [searchQuery, setSearchQuery] = useState("")

  const filteredCategories = categories.filter(
    (cat) =>
      cat.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      cat.keywords.some((k) => k.toLowerCase().includes(searchQuery.toLowerCase()))
  )

  const handleCreateCategory = (data: {
    name: string
    description: string
    keywords: string[]
    color: string
  }) => {
    const newCategory: Category = {
      id: `cat-${Date.now()}`,
      ...data,
      createdAt: new Date(),
    }
    setCategories([...categories, newCategory])
  }

  const handleDeleteCategory = (category: Category) => {
    setCategories(categories.filter((c) => c.id !== category.id))
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div className="flex flex-col gap-2">
          <h1 className="text-2xl font-bold text-foreground">Categorías</h1>
          <p className="text-muted-foreground">
            Gestiona las categorías y palabras clave para clasificación automática
          </p>
        </div>
        <Button className="gap-2" onClick={() => setIsFormOpen(true)}>
          <Plus className="h-4 w-4" />
          Nueva Categoría
        </Button>
      </div>

      <div className="relative max-w-sm">
        <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
        <Input
          placeholder="Buscar categorías o palabras clave..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="pl-9 bg-secondary border-border text-foreground placeholder:text-muted-foreground"
        />
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {filteredCategories.map((category) => (
          <CategoryCard
            key={category.id}
            category={category}
            onDelete={handleDeleteCategory}
          />
        ))}
      </div>

      {filteredCategories.length === 0 && (
        <div className="flex flex-col items-center justify-center py-12 text-center">
          <p className="text-muted-foreground mb-4">
            No se encontraron categorías
          </p>
          <Button variant="outline" onClick={() => setIsFormOpen(true)}>
            <Plus className="h-4 w-4 mr-2" />
            Crear primera categoría
          </Button>
        </div>
      )}

      <CategoryForm
        open={isFormOpen}
        onOpenChange={setIsFormOpen}
        onSubmit={handleCreateCategory}
      />
    </div>
  )
}

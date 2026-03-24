"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Edit2, Trash2 } from "lucide-react"
import type { Category } from "@/lib/types"
import { format } from "date-fns"
import { es } from "date-fns/locale"

interface CategoryCardProps {
  category: Category
  onEdit?: (category: Category) => void
  onDelete?: (category: Category) => void
}

export function CategoryCard({ category, onEdit, onDelete }: CategoryCardProps) {
  return (
    <Card className="border-border bg-card group hover:border-primary/50 transition-colors">
      <CardHeader className="flex flex-row items-start justify-between space-y-0 pb-2">
        <div className="flex items-center gap-3">
          <div
            className="h-4 w-4 rounded-full"
            style={{ backgroundColor: category.color }}
          />
          <CardTitle className="text-lg font-semibold text-foreground">
            {category.name}
          </CardTitle>
        </div>
        <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
          <Button
            variant="ghost"
            size="icon"
            className="h-8 w-8 text-muted-foreground hover:text-foreground"
            onClick={() => onEdit?.(category)}
          >
            <Edit2 className="h-4 w-4" />
          </Button>
          <Button
            variant="ghost"
            size="icon"
            className="h-8 w-8 text-muted-foreground hover:text-destructive"
            onClick={() => onDelete?.(category)}
          >
            <Trash2 className="h-4 w-4" />
          </Button>
        </div>
      </CardHeader>
      <CardContent>
        <p className="text-sm text-muted-foreground mb-4">
          {category.description}
        </p>
        <div className="flex flex-wrap gap-2 mb-4">
          {category.keywords.map((keyword) => (
            <Badge
              key={keyword}
              variant="secondary"
              className="bg-secondary text-secondary-foreground text-xs"
            >
              {keyword}
            </Badge>
          ))}
        </div>
        <p className="text-xs text-muted-foreground">
          Creada: {format(category.createdAt, "dd MMM yyyy", { locale: es })}
        </p>
      </CardContent>
    </Card>
  )
}

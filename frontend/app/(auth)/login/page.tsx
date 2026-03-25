"use client"

import { useState } from "react"
import { useRouter } from "next/navigation"
import { ShieldCheck } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { login } from "@/lib/api"

export default function LoginPage() {
  const router = useRouter()
  const [email, setEmail] = useState("admin@vulntracker.com")
  const [password, setPassword] = useState("password123")
  const [error, setError] = useState("")
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError("")
    setLoading(true)
    try {
      await login(email, password)
      router.push("/")
    } catch {
      setError("Credenciales inválidas o acceso no autorizado")
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="container relative min-h-screen flex items-center justify-center lg:max-w-none lg:grid lg:grid-cols-2 lg:px-0 bg-background">
      <div className="relative hidden h-full flex-col bg-muted p-10 text-white dark:border-r lg:flex">
        <div className="absolute inset-0 bg-[#bd103b]" />
        <div className="relative z-20 flex items-center text-lg font-medium opacity-90">
          <ShieldCheck className="mr-2 h-6 w-6" />
          Fiduprevisora Security
        </div>
        <div className="relative z-20 mt-auto">
          <blockquote className="space-y-2">
            <p className="text-xl italic font-serif">
              "Panel integral para la gestión, control y trazabilidad de vulnerabilidades reportadas, asegurando la integridad de nuestra infraestructura."
            </p>
            <footer className="text-sm">Departamento de Ciberseguridad</footer>
          </blockquote>
        </div>
      </div>
      <div className="p-8 w-full max-w-sm mx-auto">
        <div className="flex w-full flex-col justify-center space-y-6">
          <div className="flex flex-col space-y-2 text-center">
            <h1 className="text-2xl font-semibold tracking-tight">Bienvenido</h1>
            <p className="text-sm text-muted-foreground">
              Ingresa tus credenciales para acceder al panel
            </p>
          </div>
          <form onSubmit={handleSubmit}>
            <div className="grid gap-4">
              <div className="grid gap-2">
                <Label htmlFor="email">Correo electrónico</Label>
                <Input
                  id="email"
                  type="email"
                  autoCapitalize="none"
                  autoComplete="email"
                  autoCorrect="off"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                />
              </div>
              <div className="grid gap-2">
                <Label htmlFor="password">Contraseña</Label>
                <Input
                  id="password"
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                />
              </div>
              {error && (
                <p className="text-sm text-destructive text-center">{error}</p>
              )}
              <Button
                type="submit"
                disabled={loading}
                className="w-full bg-[#fa8200] hover:bg-[#fa8200]/90 text-white mt-2"
              >
                {loading ? "Verificando..." : "Ingresar al Panel"}
              </Button>
            </div>
          </form>
        </div>
      </div>
    </div>
  )
}

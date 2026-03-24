import { Metadata } from "next"
import Link from "next/link"
import { ShieldCheck } from "lucide-react"

import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"

export const metadata: Metadata = {
  title: "Iniciar sesión | fiduprevisora",
  description: "Accede al panel de control de vulnerabilidades.",
}

export default function LoginPage() {
  return (
    <div className="container relative min-h-screen flex items-center justify-center lg:max-w-none lg:grid lg:grid-cols-2 lg:px-0 bg-background">
      <div className="relative hidden h-full flex-col bg-muted p-10 text-white dark:border-r lg:flex">
        <div className="absolute inset-0 bg-[#bd103b]" /> {/* Fiduprevisora red aesthetic */}
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
            <h1 className="text-2xl font-semibold tracking-tight">
              Bienvenido
            </h1>
            <p className="text-sm text-muted-foreground">
              Ingresa tus credenciales para acceder al panel
            </p>
          </div>
          <div className="grid gap-6">
            <form>
              <div className="grid gap-4">
                <div className="grid gap-2">
                  <Label htmlFor="email">Correo electrónico</Label>
                  <Input
                    id="email"
                    placeholder="admin@vulntracker.com"
                    type="email"
                    autoCapitalize="none"
                    autoComplete="email"
                    autoCorrect="off"
                    defaultValue="admin@vulntracker.com"
                  />
                </div>
                <div className="grid gap-2">
                  <Label htmlFor="password">Contraseña</Label>
                  <Input
                    id="password"
                    type="password"
                    defaultValue="password123"
                  />
                </div>
                <Button asChild className="w-full bg-[#fa8200] hover:bg-[#fa8200]/90 text-white mt-2">
                  <Link href="/">
                    Ingresar al Panel
                  </Link>
                </Button>
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>
  )
}

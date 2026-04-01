"use client"

import { useEffect, useState } from "react"
import { useSearchParams } from "next/navigation"
import { ShieldCheck, CheckCircle2, XCircle, Loader2 } from "lucide-react"
import { verifyEmail } from "@/lib/api"

type Status = "loading" | "success" | "error"

export default function VerifyPage() {
  const searchParams = useSearchParams()
  const token = searchParams.get("token")

  const [status, setStatus] = useState<Status>(token ? "loading" : "error")
  const [message, setMessage] = useState(
    token ? "Verificando tu email..." : "Token no proporcionado en la URL."
  )

  useEffect(() => {
    if (!token) return

    verifyEmail(token)
      .then(() => {
        setStatus("success")
        setMessage("¡Email verificado exitosamente! Ya podés continuar la conversación en WhatsApp.")
      })
      .catch(() => {
        setStatus("error")
        setMessage("El token es inválido o expiró. Pedí un nuevo email de verificación desde WhatsApp.")
      })
  }, [token])

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
              &ldquo;Panel integral para la gestión, control y trazabilidad de
              vulnerabilidades reportadas, asegurando la integridad de nuestra
              infraestructura.&rdquo;
            </p>
            <footer className="text-sm">Departamento de Ciberseguridad</footer>
          </blockquote>
        </div>
      </div>

      <div className="p-8 w-full max-w-sm mx-auto">
        <div className="flex w-full flex-col items-center justify-center space-y-6 text-center">
          {status === "loading" && (
            <Loader2 className="h-16 w-16 animate-spin text-[#fa8200]" />
          )}
          {status === "success" && (
            <CheckCircle2 className="h-16 w-16 text-[#25D366]" />
          )}
          {status === "error" && (
            <XCircle className="h-16 w-16 text-destructive" />
          )}

          <h1 className="text-2xl font-semibold tracking-tight">
            {status === "loading" && "Verificando..."}
            {status === "success" && "Verificación exitosa"}
            {status === "error" && "Error de verificación"}
          </h1>

          <p className="text-sm text-muted-foreground">{message}</p>

          {status === "success" && (
            <p className="text-xs text-muted-foreground">
              Podés cerrar esta pestaña.
            </p>
          )}
        </div>
      </div>
    </div>
  )
}

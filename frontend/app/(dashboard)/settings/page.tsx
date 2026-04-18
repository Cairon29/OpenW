"use client"

import { useEffect, useState, useCallback } from "react"
import {
  Settings,
  MessageSquare,
  Mail,
  SlidersHorizontal,
  ToggleLeft,
  Globe,
  Loader2,
  RefreshCw,
} from "lucide-react"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { PageHeader } from "@/components/dashboard/page-header"
import { SettingsField } from "@/components/dashboard/settings-field"
import { ConnectionCard } from "@/components/dashboard/settings-connection-card"
import { getConfigurations } from "@/lib/api"
import type { ConfigsByCategory, SystemConfig } from "@/lib/types"

// ── Tab metadata ──────────────────────────────────────────────────────────────

const TABS = [
  { id: "general",       label: "General",          icon: Settings },
  { id: "whatsapp",      label: "WhatsApp",          icon: MessageSquare },
  { id: "email",         label: "Correo",            icon: Mail },
  { id: "analysis",      label: "Análisis",          icon: SlidersHorizontal },
  { id: "modules",       label: "Módulos",           icon: ToggleLeft },
  { id: "external_apis", label: "APIs externas",     icon: Globe },
] as const

type TabId = typeof TABS[number]["id"]

// ── Helpers ───────────────────────────────────────────────────────────────────

function filterByCategory(configs: ConfigsByCategory, category: string): SystemConfig[] {
  return configs[category as keyof ConfigsByCategory] ?? []
}

// ── Page ──────────────────────────────────────────────────────────────────────

export default function SettingsPage() {
  const [configs, setConfigs] = useState<ConfigsByCategory>({})
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [activeTab, setActiveTab] = useState<TabId>("general")

  const load = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const data = await getConfigurations()
      setConfigs(data)
    } catch {
      setError("No se pudieron cargar las configuraciones. Verifica que el backend esté activo.")
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => { load() }, [load])

  function handleSaved(updated: SystemConfig) {
    setConfigs((prev) => {
      const cat = updated.category as keyof ConfigsByCategory
      const list = (prev[cat] ?? []).map((c) => (c.key === updated.key ? updated : c))
      return { ...prev, [cat]: list }
    })
  }

  return (
    <div className="flex flex-col gap-6 p-6">
      <div className="flex items-center justify-between">
        <PageHeader
          icon={Settings}
          title="Configuración del sistema"
          description="Administra parámetros globales, credenciales y módulos del sistema de forma centralizada."
        />
        <Button variant="outline" size="sm" onClick={load} disabled={loading} className="gap-2">
          <RefreshCw className={`h-4 w-4 ${loading ? "animate-spin" : ""}`} />
          Actualizar
        </Button>
      </div>

      {error && (
        <div className="rounded-md bg-destructive/10 text-destructive text-sm px-4 py-3">
          {error}
        </div>
      )}

      <Tabs value={activeTab} onValueChange={(v) => setActiveTab(v as TabId)}>
        <TabsList className="flex-wrap h-auto gap-1 bg-muted/50 p-1">
          {TABS.map((tab) => (
            <TabsTrigger
              key={tab.id}
              value={tab.id}
              className="gap-1.5 data-[state=active]:bg-[#fa8200] data-[state=active]:text-white"
            >
              <tab.icon className="h-3.5 w-3.5" />
              {tab.label}
            </TabsTrigger>
          ))}
        </TabsList>

        {/* ── General ────────────────────────────────────────────────────── */}
        <TabsContent value="general">
          <ConfigCard
            title="Parámetros generales"
            description="Nombre del sistema, organización, URLs y comportamientos globales."
            fields={filterByCategory(configs, "general")}
            loading={loading}
            onSaved={handleSaved}
          />
        </TabsContent>

        {/* ── WhatsApp ───────────────────────────────────────────────────── */}
        <TabsContent value="whatsapp" className="space-y-4">
          <ConfigCard
            title="Credenciales de WhatsApp Cloud API"
            description="Configuración de la integración con Meta WhatsApp Business. Modifica con cuidado — un token incorrecto desactiva el bot."
            fields={filterByCategory(configs, "whatsapp")}
            loading={loading}
            onSaved={handleSaved}
          />
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-base">Prueba de conexión</CardTitle>
              <CardDescription>Verifica que las credenciales de WhatsApp sean válidas.</CardDescription>
            </CardHeader>
            <CardContent>
              <ConnectionCard
                service="whatsapp"
                label="WhatsApp Cloud API"
                description="Consulta el número registrado en Meta Business para validar el token de acceso."
                icon={<MessageSquare className="h-5 w-5" />}
              />
            </CardContent>
          </Card>
        </TabsContent>

        {/* ── Email ──────────────────────────────────────────────────────── */}
        <TabsContent value="email" className="space-y-4">
          <ConfigCard
            title="Configuración de correo SMTP"
            description="Credenciales de Gmail para el envío de correos de verificación a nuevos usuarios del bot."
            fields={filterByCategory(configs, "email")}
            loading={loading}
            onSaved={handleSaved}
          />
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-base">Prueba de conexión</CardTitle>
              <CardDescription>Verifica que las credenciales SMTP sean válidas.</CardDescription>
            </CardHeader>
            <CardContent>
              <ConnectionCard
                service="email"
                label="Gmail SMTP"
                description="Intenta autenticar con las credenciales configuradas contra el servidor SMTP de Google."
                icon={<Mail className="h-5 w-5" />}
              />
            </CardContent>
          </Card>
        </TabsContent>

        {/* ── Analysis ───────────────────────────────────────────────────── */}
        <TabsContent value="analysis">
          <ConfigCard
            title="Reglas de análisis"
            description="Define thresholds de severidad, palabras clave y comportamientos del motor de clasificación."
            fields={filterByCategory(configs, "analysis")}
            loading={loading}
            onSaved={handleSaved}
          />
        </TabsContent>

        {/* ── Modules ────────────────────────────────────────────────────── */}
        <TabsContent value="modules">
          <Card>
            <CardHeader>
              <CardTitle className="text-base">Activación de módulos</CardTitle>
              <CardDescription>
                Activa o desactiva funcionalidades del sistema sin necesidad de reiniciarlo.
                Los cambios se aplican inmediatamente.
              </CardDescription>
            </CardHeader>
            <CardContent>
              {loading ? (
                <LoadingSkeleton />
              ) : filterByCategory(configs, "modules").length === 0 ? (
                <EmptyState />
              ) : (
                <div className="divide-y divide-border/50">
                  {filterByCategory(configs, "modules").map((cfg) => (
                    <SettingsField key={cfg.key} config={cfg} onSaved={handleSaved} />
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* ── External APIs ───────────────────────────────────────────────── */}
        <TabsContent value="external_apis" className="space-y-4">
          <ConfigCard
            title="APIs externas"
            description="Credenciales de servicios de terceros como VirusTotal (análisis de indicadores) y Deepseek (validación con IA)."
            fields={filterByCategory(configs, "external_apis")}
            loading={loading}
            onSaved={handleSaved}
          />
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-base">Prueba de conexiones</CardTitle>
              <CardDescription>Verifica que las API Keys externas sean válidas.</CardDescription>
            </CardHeader>
            <CardContent className="space-y-3">
              <ConnectionCard
                service="virustotal"
                label="VirusTotal"
                description="Valida la API Key contra el endpoint de análisis de IPs de VirusTotal."
                icon={<Globe className="h-5 w-5" />}
              />
              <ConnectionCard
                service="deepseek"
                label="Deepseek AI"
                description="Verifica la API Key y consulta el balance de créditos disponibles."
                icon={<SlidersHorizontal className="h-5 w-5" />}
              />
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}

// ── Shared sub-components ─────────────────────────────────────────────────────

function ConfigCard({
  title,
  description,
  fields,
  loading,
  onSaved,
}: {
  title: string
  description: string
  fields: SystemConfig[]
  loading: boolean
  onSaved: (updated: SystemConfig) => void
}) {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-base">{title}</CardTitle>
        <CardDescription>{description}</CardDescription>
      </CardHeader>
      <CardContent>
        {loading ? (
          <LoadingSkeleton />
        ) : fields.length === 0 ? (
          <EmptyState />
        ) : (
          <div>
            {fields.map((cfg) => (
              <SettingsField key={cfg.key} config={cfg} onSaved={onSaved} />
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  )
}

function LoadingSkeleton() {
  return (
    <div className="flex items-center justify-center py-8 gap-2 text-muted-foreground">
      <Loader2 className="h-4 w-4 animate-spin" />
      <span className="text-sm">Cargando configuraciones...</span>
    </div>
  )
}

function EmptyState() {
  return (
    <p className="text-sm text-muted-foreground text-center py-6">
      No hay configuraciones disponibles en esta sección.
    </p>
  )
}

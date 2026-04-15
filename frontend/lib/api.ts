import type { VulnerabilityCase, Category, Severity, ConfigsByCategory, SystemConfig, ConnectionTestResult } from "@/lib/types"

const API_URL = ""

// ── Mappers ──────────────────────────────────────────────────────────────────

function mapNovedad(n: Record<string, unknown>): VulnerabilityCase {
  const severityMap: Record<string, Severity> = {
    critica: "critical",
    alta: "high",
    media: "medium",
    baja: "low",
    informativa: "low",
  }
  const statusMap: Record<string, VulnerabilityCase["status"]> = {
    abierta: "open",
    en_proceso: "in_progress",
    resuelta: "resolved",
    descartada: "closed",
  }
  const creador = n.creador as Record<string, unknown> | null
  const categoria = n.categoria as Record<string, unknown> | null

  return {
    id: `VULN-${String(n.id).padStart(3, "0")}`,
    title: String(n.titulo ?? ""),
    description: String(n.descripcion ?? ""),
    severity: severityMap[String(n.severidad)] ?? "medium",
    status: statusMap[String(n.estado)] ?? "open",
    reportedBy: creador ? String(creador.name ?? "Desconocido") : "Desconocido",
    reportedAt: new Date(String(n.fecha_registro)),
    category: categoria ? String(categoria.nombre ?? "Sin categoría") : "Sin categoría",
    keywords: [],
    whatsappNumber: String(n.user_phone ?? ""),
    lastUpdated: new Date(String(n.fecha_registro)),
  }
}

function mapCategoria(c: Record<string, unknown>): Category {
  return {
    id: String(c.id),
    name: String(c.nombre ?? ""),
    description: String(c.descripcion ?? ""),
    keywords: c.palabra_clave ? [String(c.palabra_clave)] : [],
    createdAt: new Date(String(c.created_at)),
    color: "#3b82f6",
  }
}

// ── Novedades ─────────────────────────────────────────────────────────────────

export async function createNovedad(data: {
  titulo: string
  descripcion: string
  severidad: string
  estado: string
  categoria_id?: number | null
  user_phone?: number | null
}): Promise<VulnerabilityCase> {
  const res = await fetch(`${API_URL}/api/v1/novedades/novedades`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  })
  if (!res.ok) throw new Error("Error al crear el caso")
  const created = await res.json()
  return mapNovedad(created as Record<string, unknown>)
}

export async function getNovedades(): Promise<VulnerabilityCase[]> {
  const res = await fetch(`${API_URL}/api/v1/novedades/novedades`)
  if (!res.ok) throw new Error("Error al obtener novedades")
  const data = await res.json()
  return (data as Record<string, unknown>[]).map(mapNovedad)
}

// ── Categorías ────────────────────────────────────────────────────────────────

export async function getCategorias(): Promise<Category[]> {
  const res = await fetch(`${API_URL}/api/v1/categorias/categorias`)
  if (!res.ok) throw new Error("Error al obtener categorías")
  const data = await res.json()
  return (data as Record<string, unknown>[]).map(mapCategoria)
}

export async function createCategoria(data: {
  name: string
  description: string
  keywords: string[]
}): Promise<Category> {
  const res = await fetch(`${API_URL}/api/v1/categorias/categorias`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      categoria: data.name,
      descripcion: data.description,
      palabra_clave: data.keywords[0] ?? null,
    }),
  })
  if (!res.ok) throw new Error("Error al crear categoría")
  const created = await res.json()
  return mapCategoria(created as Record<string, unknown>)
}

export async function deleteCategoria(id: string): Promise<void> {
  const res = await fetch(`${API_URL}/api/v1/categorias/categorias/${id}`, {
    method: "DELETE",
  })
  if (!res.ok) throw new Error("Error al eliminar categoría")
}

// ── Bot / Conversaciones ──────────────────────────────────────────────────────

export interface BotMessage {
  role: "user" | "bot"
  text: string
  time: string
}

export interface BotConversation {
  phone: string
  bot_active: boolean
  last_message: string
  last_time: string
  messages: BotMessage[]
  profile_name?: string | null
  profile_photo_url?: string | null
}

export async function getBotConversations(): Promise<BotConversation[]> {
  const res = await fetch(`${API_URL}/api/v1/chat/bot/conversations`)
  if (!res.ok) throw new Error("Error al obtener conversaciones")
  return res.json()
}

export async function toggleBot(phone: string): Promise<{ phone: string; bot_active: boolean }> {
  const res = await fetch(`${API_URL}/api/v1/chat/bot/toggle`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ phone }),
  })
  if (!res.ok) throw new Error("Error al cambiar estado del bot")
  return res.json()
}

export async function sendManualMessage(phone: string, message: string): Promise<void> {
  const res = await fetch(`${API_URL}/api/v1/chat/bot/send`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ phone, message }),
  })
  if (!res.ok) throw new Error("Error al enviar mensaje")
}

// ── Dashboard Metrics ─────────────────────────────────────────────────────────

export interface DashboardMetricsAPI {
  totalCases: number
  openCases: number
  resolvedToday: number
  criticalOpen: number
  bySeverity: Record<string, number>
  byStatus: Record<string, number>
  recentTrend: { date: string; count: number }[]
}

export interface BotMetricsAPI {
  totalConversations: number
  botMessages: number
  responseRate: number
  usageOverTime: { date: string; count: number }[]
  effectiveness: { conContexto: number; sinContexto: number }
}

export async function getDashboardMetrics(): Promise<DashboardMetricsAPI> {
  const res = await fetch(`${API_URL}/api/v1/novedades/dashboard/metrics`)
  if (!res.ok) throw new Error("Error al obtener métricas del dashboard")
  return res.json()
}

export async function getBotMetrics(): Promise<BotMetricsAPI> {
  const res = await fetch(`${API_URL}/api/v1/chat/bot/metrics`)
  if (!res.ok) throw new Error("Error al obtener métricas del bot")
  return res.json()
}

// ── Verificación de email (onboarding WhatsApp) ─────────────────────────────

export async function verifyEmail(token: string): Promise<{ status: string }> {
  const res = await fetch(
    `${API_URL}/api/v1/auth/verify-email?token=${encodeURIComponent(token)}`
  )
  if (!res.ok) throw new Error("Token inválido o expirado")
  return res.json()
}

// ── Configuración del sistema ─────────────────────────────────────────────────

export async function getConfigurations(category?: string): Promise<ConfigsByCategory> {
  const url = category
    ? `${API_URL}/api/v1/configuracion?category=${encodeURIComponent(category)}`
    : `${API_URL}/api/v1/configuracion`
  const res = await fetch(url, { cache: "no-store" })
  if (!res.ok) throw new Error("Error al obtener configuraciones")
  return res.json()
}

export async function updateConfiguration(
  key: string,
  value: string,
  updatedBy?: string
): Promise<SystemConfig> {
  const res = await fetch(`${API_URL}/api/v1/configuracion/${key}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ value, updated_by: updatedBy }),
  })
  if (!res.ok) throw new Error("Error al actualizar configuración")
  return res.json()
}

export async function bulkUpdateConfigurations(
  items: { key: string; value: string }[],
  updatedBy?: string
): Promise<{ updated: number; items: SystemConfig[] }> {
  const res = await fetch(`${API_URL}/api/v1/configuracion/bulk`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ items, updated_by: updatedBy }),
  })
  if (!res.ok) throw new Error("Error al guardar configuraciones")
  return res.json()
}

export async function testConnection(service: string): Promise<ConnectionTestResult> {
  const res = await fetch(`${API_URL}/api/v1/configuracion/test/${service}`, {
    method: "POST",
  })
  if (!res.ok) throw new Error("Error al probar conexión")
  return res.json()
}

// ── Auth ──────────────────────────────────────────────────────────────────────

export async function login(
  email: string,
  password: string
): Promise<Record<string, unknown>> {
  const res = await fetch(`${API_URL}/api/v1/users/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
  })
  if (!res.ok) throw new Error("Credenciales inválidas o acceso no autorizado")
  return res.json()
}

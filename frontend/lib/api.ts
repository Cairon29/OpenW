import type { VulnerabilityCase, Category, Severity } from "@/lib/types"

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:2222"

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

export async function getNovedades(): Promise<VulnerabilityCase[]> {
  const res = await fetch(`${API_URL}/api/novedades/novedades`)
  if (!res.ok) throw new Error("Error al obtener novedades")
  const data = await res.json()
  return (data as Record<string, unknown>[]).map(mapNovedad)
}

// ── Categorías ────────────────────────────────────────────────────────────────

export async function getCategorias(): Promise<Category[]> {
  const res = await fetch(`${API_URL}/api/categorias/categorias`)
  if (!res.ok) throw new Error("Error al obtener categorías")
  const data = await res.json()
  return (data as Record<string, unknown>[]).map(mapCategoria)
}

export async function createCategoria(data: {
  name: string
  description: string
  keywords: string[]
}): Promise<Category> {
  const res = await fetch(`${API_URL}/api/categorias/categorias`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      nombre: data.name,
      descripcion: data.description,
      palabra_clave: data.keywords[0] ?? null,
    }),
  })
  if (!res.ok) throw new Error("Error al crear categoría")
  const created = await res.json()
  return mapCategoria(created as Record<string, unknown>)
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
}

export async function getBotConversations(): Promise<BotConversation[]> {
  const res = await fetch(`${API_URL}/api/novedades/bot/conversations`)
  if (!res.ok) throw new Error("Error al obtener conversaciones")
  return res.json()
}

export async function toggleBot(phone: string): Promise<{ phone: string; bot_active: boolean }> {
  const res = await fetch(`${API_URL}/api/novedades/bot/toggle`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ phone }),
  })
  if (!res.ok) throw new Error("Error al cambiar estado del bot")
  return res.json()
}

export async function sendManualMessage(phone: string, message: string): Promise<void> {
  const res = await fetch(`${API_URL}/api/novedades/bot/send`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ phone, message }),
  })
  if (!res.ok) throw new Error("Error al enviar mensaje")
}

// ── Auth ──────────────────────────────────────────────────────────────────────

export async function login(
  email: string,
  password: string
): Promise<Record<string, unknown>> {
  const res = await fetch(`${API_URL}/api/users/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
  })
  if (!res.ok) throw new Error("Credenciales inválidas o acceso no autorizado")
  return res.json()
}

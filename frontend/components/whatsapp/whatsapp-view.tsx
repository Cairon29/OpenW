"use client"

import * as React from "react"
import { Search, Archive, Filter, Paperclip, Send, Sparkles, User, BarChart2, MessageSquare } from "lucide-react"
import { Avatar, AvatarFallback } from "@/components/ui/avatar"
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Switch } from "@/components/ui/switch"
import { Badge } from "@/components/ui/badge"
import { getBotConversations, toggleBot, sendManualMessage, type BotConversation } from "@/lib/api"

function formatTime(isoString: string): string {
  if (!isoString) return ""
  try {
    const date = new Date(isoString)
    const now = new Date()
    const diffMs = now.getTime() - date.getTime()
    const diffH = diffMs / (1000 * 60 * 60)
    if (diffH < 1) return `${Math.floor(diffMs / 60000)}m`
    if (diffH < 24) return `${Math.floor(diffH)}h`
    return date.toLocaleDateString("es-CO", { day: "2-digit", month: "2-digit" })
  } catch {
    return ""
  }
}

function getInitials(phone: string): string {
  return phone.slice(-2)
}

export function WhatsAppView() {
  const [conversations, setConversations] = React.useState<BotConversation[]>([])
  const [selectedPhone, setSelectedPhone] = React.useState<string | null>(null)
  const [manualMessage, setManualMessage] = React.useState("")
  const [sending, setSending] = React.useState(false)
  const messagesEndRef = React.useRef<HTMLDivElement>(null)

  const selectedConv = conversations.find(c => c.phone === selectedPhone) ?? null
  const isBotOn = selectedConv?.bot_active ?? true

  // Fetch conversations and poll every 4 seconds
  React.useEffect(() => {
    fetchConversations()
    const interval = setInterval(fetchConversations, 4000)
    return () => clearInterval(interval)
  }, [])

  // Auto-scroll to bottom when messages change
  React.useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }, [selectedConv?.messages.length])

  async function fetchConversations() {
    try {
      const data = await getBotConversations()
      setConversations(data)
      // Auto-select first conversation if none selected
      if (!selectedPhone && data.length > 0) {
        setSelectedPhone(data[0].phone)
      }
    } catch {
      // Silent fail - backend may not be running
    }
  }

  async function handleToggleBot() {
    if (!selectedPhone) return
    try {
      const result = await toggleBot(selectedPhone)
      setConversations(prev =>
        prev.map(c => c.phone === selectedPhone ? { ...c, bot_active: result.bot_active } : c)
      )
    } catch (e) {
      console.error("Error toggling bot:", e)
    }
  }

  async function handleSendMessage() {
    if (!selectedPhone || !manualMessage.trim() || sending) return
    setSending(true)
    try {
      await sendManualMessage(selectedPhone, manualMessage.trim())
      setManualMessage("")
      await fetchConversations()
    } catch (e) {
      console.error("Error enviando mensaje:", e)
    } finally {
      setSending(false)
    }
  }

  async function handleKeyDown(e: React.KeyboardEvent) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault()
      await handleSendMessage()
    }
  }

  return (
    <div className="flex h-full w-full bg-background relative overflow-hidden">
      {/* Left Sidebar - Chat List */}
      <div className="w-full md:w-[35%] lg:w-[30%] min-w-[320px] max-w-[450px] flex-col h-full bg-background border-r border-border shrink-0 hidden md:flex z-10 min-h-0">
        <div className="p-3 border-b border-border flex flex-col gap-3 shrink-0">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-semibold px-1">Chats</h2>
            <div className="flex items-center gap-1 text-muted-foreground mr-1">
              <Button variant="ghost" size="icon" className="h-8 w-8 hover:bg-muted">
                <Archive className="h-4 w-4" />
              </Button>
              <Button variant="ghost" size="icon" className="h-8 w-8 hover:bg-muted">
                <Filter className="h-4 w-4" />
              </Button>
              <Badge variant="secondary" className="px-1.5 min-w-6 justify-center text-xs">
                {conversations.length}
              </Badge>
            </div>
          </div>
          <div className="relative mx-1">
            <Search className="absolute left-2.5 top-2 h-4 w-4 text-muted-foreground" />
            <Input
              type="search"
              placeholder="Buscar..."
              className="pl-9 bg-muted/50 border-none h-8 text-sm"
            />
          </div>
        </div>

        <ScrollArea className="flex-1 min-h-0">
          {conversations.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-40 gap-2 text-muted-foreground p-4">
              <MessageSquare className="h-8 w-8 opacity-30" />
              <p className="text-xs text-center">Aún no hay conversaciones.<br />Cuando alguien escriba al bot aparecerán aquí.</p>
            </div>
          ) : (
            <div className="flex flex-col">
              {conversations.map((conv) => {
                const isActive = conv.phone === selectedPhone
                const badgeLabel = conv.bot_active ? "IA" : "H"
                const badgeColor = conv.bot_active
                  ? "text-blue-500 bg-blue-50 dark:bg-blue-950/50"
                  : "text-orange-500 bg-orange-50 dark:bg-orange-950/50"

                return (
                  <div
                    key={conv.phone}
                    onClick={() => setSelectedPhone(conv.phone)}
                    className={`flex items-start gap-3 p-3 cursor-pointer hover:bg-accent transition-colors ${isActive ? "bg-accent/50 dark:bg-accent/30" : ""}`}
                  >
                    <Avatar className="h-10 w-10 border-2 border-background shadow-sm mt-0.5 shrink-0">
                      <AvatarFallback className="bg-emerald-600 text-white font-medium text-sm">
                        {getInitials(conv.phone)}
                      </AvatarFallback>
                    </Avatar>
                    <div className="flex-1 space-y-1 min-w-0 pr-1">
                      <div className="flex items-center justify-between">
                        <p className="text-[13px] font-medium leading-tight truncate pr-2">+{conv.phone}</p>
                        <span className="text-[11px] text-muted-foreground whitespace-nowrap shrink-0">
                          {formatTime(conv.last_time)}
                        </span>
                      </div>
                      <div className="flex items-center justify-between gap-2 mt-0.5">
                        <p className="text-[12px] text-muted-foreground truncate">{conv.last_message}</p>
                        <span className={`text-[9px] font-bold px-1.5 py-0.5 rounded-[4px] shrink-0 ${badgeColor}`}>
                          {badgeLabel}
                        </span>
                      </div>
                    </div>
                  </div>
                )
              })}
            </div>
          )}
        </ScrollArea>
      </div>

      {/* Right Area - Chat Content */}
      <div className="flex-1 flex flex-col h-full bg-[#f0f2f5] dark:bg-zinc-950/50 min-w-0 min-h-0 relative">

        {!selectedConv ? (
          // Empty state
          <div className="flex-1 flex flex-col items-center justify-center gap-3 text-muted-foreground">
            <MessageSquare className="h-12 w-12 opacity-20" />
            <p className="text-sm">Selecciona una conversación</p>
          </div>
        ) : (
          <>
            {/* Chat Header */}
            <div className="h-[60px] px-3 md:px-5 border-b border-border bg-background flex items-center justify-between shrink-0 sticky top-0 z-20 shadow-sm">
              <div className="flex items-center gap-3 w-full max-w-[50%]">
                <div className="relative shrink-0">
                  <Avatar className="h-9 w-9">
                    <AvatarFallback className="bg-emerald-600 text-white font-medium text-sm">
                      {getInitials(selectedConv.phone)}
                    </AvatarFallback>
                  </Avatar>
                  <div className="absolute right-0 bottom-0 w-2.5 h-2.5 bg-green-500 rounded-full border-2 border-background"></div>
                </div>
                <div className="flex flex-col justify-center min-w-0">
                  <span className="font-semibold text-[13px] truncate">+{selectedConv.phone}</span>
                  <div className="flex items-center gap-2 text-[11px] text-muted-foreground mt-0.5">
                    <span className="truncate">{selectedConv.messages.length} mensajes</span>
                  </div>
                </div>
              </div>

              <div className="flex items-center gap-1.5 md:gap-2.5 shrink-0">
                <Badge variant="outline" className="hidden sm:flex gap-1 bg-emerald-50 dark:bg-emerald-950/30 text-emerald-600 border-emerald-200 text-xs px-2 py-0.5">
                  <BarChart2 className="h-3 w-3" />
                  <span>{selectedConv.messages.length}</span>
                </Badge>
                <Button variant="ghost" size="icon" className="h-8 w-8 text-muted-foreground hidden sm:flex">
                  <User className="h-4 w-4" />
                </Button>
                {isBotOn && (
                  <Button
                    variant="outline"
                    size="sm"
                    className="bg-background h-8 text-xs px-2 md:px-3"
                    onClick={handleToggleBot}
                  >
                    <span className="hidden sm:inline">Intervenir</span>
                    <span className="sm:hidden">Int.</span>
                  </Button>
                )}
                <div className={`flex items-center gap-1.5 md:gap-2 px-2 md:px-2.5 py-1.5 rounded-md border text-xs transition-colors ${
                  isBotOn
                    ? "bg-indigo-50 dark:bg-indigo-950/30 text-indigo-600 dark:text-indigo-400 border-indigo-100 dark:border-indigo-900/50"
                    : "bg-muted text-muted-foreground border-border"
                }`}>
                  <span className="font-medium whitespace-nowrap">IA <span className="hidden sm:inline">{isBotOn ? "ON" : "OFF"}</span></span>
                  <Switch
                    checked={isBotOn}
                    onCheckedChange={handleToggleBot}
                    className="data-[state=checked]:bg-indigo-600 scale-[0.7] sm:scale-[0.8]"
                  />
                </div>
              </div>
            </div>

            {/* Chat Messages */}
            <ScrollArea className="flex-1 min-h-0 w-full">
              <div className="flex flex-col gap-3 w-full px-4 md:px-8 lg:px-12 py-6">
                {selectedConv.messages.map((msg, idx) => {
                  const isUser = msg.role === "user"
                  return (
                    <div key={idx} className={`flex w-full ${isUser ? "justify-start" : "justify-end"}`}>
                      <div className={`max-w-[85%] md:max-w-[75%] lg:max-w-[65%] rounded-2xl px-3.5 py-2 relative shadow-sm ${
                        isUser
                          ? "bg-background border border-border rounded-tl-sm"
                          : "bg-[#dcf8c6] dark:bg-emerald-900/90 text-emerald-950 dark:text-emerald-50 rounded-tr-sm border border-emerald-200/60 dark:border-emerald-800"
                      }`}>
                        {!isUser && (
                          <div className="flex items-center gap-1 mb-0.5 opacity-70">
                            <Sparkles className="h-[10px] w-[10px]" />
                            <span className="text-[9px] uppercase font-bold tracking-wider">IA</span>
                          </div>
                        )}
                        <p className="text-[14px] leading-relaxed whitespace-pre-wrap break-words">{msg.text}</p>
                        <div className={`text-[10px] mt-0.5 text-right ${isUser ? "text-muted-foreground" : "text-emerald-700/70 dark:text-emerald-400/70"}`}>
                          {formatTime(msg.time)}
                        </div>
                      </div>
                    </div>
                  )
                })}
                <div ref={messagesEndRef} />
              </div>
            </ScrollArea>

            {/* Chat Input */}
            <div className="p-2 md:p-3 bg-background border-t border-border shrink-0 z-20 w-full shadow-[0_-4px_10px_rgba(0,0,0,0.02)]">
              {isBotOn ? (
                <div className="flex flex-col sm:flex-row items-center justify-between gap-3 px-2 py-1">
                  <div className="text-[13px] font-medium text-indigo-600 dark:text-indigo-400 flex items-center gap-1.5 flex-1 min-w-0">
                    <Sparkles className="h-4 w-4 shrink-0" />
                    <span className="truncate">El Bot IA está respondiendo automáticamente</span>
                  </div>
                  <Button
                    variant="outline"
                    size="sm"
                    className="h-8 text-xs bg-background hover:bg-muted shrink-0 w-full sm:w-auto"
                    onClick={handleToggleBot}
                  >
                    Responder manualmente
                  </Button>
                </div>
              ) : (
                <div className="flex items-end gap-2 relative w-full">
                  <div className="relative flex-1 min-w-0">
                    <Input
                      value={manualMessage}
                      onChange={(e) => setManualMessage(e.target.value)}
                      onKeyDown={handleKeyDown}
                      className="min-h-[44px] text-[14px] w-full rounded-[22px] pr-10 pl-4 py-2.5 bg-muted/50 border-transparent hover:border-border focus-visible:ring-1 focus-visible:ring-emerald-500 shadow-none transition-all"
                      placeholder="Escribe un mensaje manual..."
                      disabled={sending}
                    />
                    <Button
                      variant="ghost"
                      size="icon"
                      className="absolute right-1 top-1/2 -translate-y-1/2 h-8 w-8 text-muted-foreground hover:text-foreground"
                    >
                      <Paperclip className="h-4 w-4" />
                    </Button>
                  </div>
                  <Button
                    onClick={handleSendMessage}
                    disabled={sending || !manualMessage.trim()}
                    className="h-[44px] w-[44px] rounded-full shrink-0 bg-emerald-600 hover:bg-emerald-700 text-white shadow-sm transition-transform active:scale-95"
                  >
                    <Send className="h-4 w-4 ml-0.5" />
                  </Button>
                </div>
              )}
            </div>
          </>
        )}
      </div>
    </div>
  )
}

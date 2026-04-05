"use client"

import * as React from "react"
import { getBotConversations, toggleBot, sendManualMessage, type BotConversation } from "@/lib/api"
import { ConversationList } from "./conversation-list"
import { ChatPanel } from "./chat-panel"
import { ContactProfileModal } from "./contact-profile-modal"

export function WhatsAppView() {
  const [conversations, setConversations] = React.useState<BotConversation[]>([])
  const [selectedPhone, setSelectedPhone] = React.useState<string | null>(null)
  const [manualMessage, setManualMessage] = React.useState("")
  const [sending, setSending] = React.useState(false)
  const [profileModalOpen, setProfileModalOpen] = React.useState(false)
  const messagesEndRef = React.useRef<HTMLDivElement>(null)

  const selectedConv = conversations.find(c => c.phone === selectedPhone) ?? null
  const isBotOn = selectedConv?.bot_active ?? true

  React.useEffect(() => {
    fetchConversations()
    const interval = setInterval(fetchConversations, 4000)
    return () => clearInterval(interval)
  }, [])

  React.useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }, [selectedConv?.messages.length])

  async function fetchConversations() {
    try {
      const data = await getBotConversations()
      setConversations(data)
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
      <ConversationList
        conversations={conversations}
        selectedPhone={selectedPhone}
        onSelectPhone={setSelectedPhone}
      />

      <ChatPanel
        conversation={selectedConv}
        isBotOn={isBotOn}
        manualMessage={manualMessage}
        sending={sending}
        messagesEndRef={messagesEndRef}
        onToggleBot={handleToggleBot}
        onMessageChange={setManualMessage}
        onSendMessage={handleSendMessage}
        onKeyDown={handleKeyDown}
        onOpenProfileModal={() => setProfileModalOpen(true)}
      />

      <ContactProfileModal
        open={profileModalOpen}
        onOpenChange={setProfileModalOpen}
        conversation={selectedConv}
      />
    </div>
  )
}

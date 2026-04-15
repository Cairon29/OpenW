"use client"

import { useState, useEffect, useRef } from "react";
import { toggleBot, sendManualMessage } from "@/lib/api"
import { useBotConversationsStream } from "@/hooks/use-bot-conversations-stream"
import { ConversationList } from "./conversation-list"
import { ChatPanel } from "./chat-panel"
import { ContactProfileModal } from "./contact-profile-modal"

export function WhatsAppView() {
  const { conversations } = useBotConversationsStream()
  const [selectedPhone, setSelectedPhone] = useState<string | null>(null)
  const [manualMessage, setManualMessage] = useState("")
  const [sending, setSending] = useState(false)
  const [profileModalOpen, setProfileModalOpen] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const selectedConv = conversations.find(c => c.phone === selectedPhone) ?? null
  const isBotOn = selectedConv?.bot_active ?? true

  useEffect(() => {
    if (!selectedPhone && conversations.length > 0) {
      setSelectedPhone(conversations[0].phone)
    }
  }, [conversations, selectedPhone])

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }, [selectedConv?.messages.length])

  async function handleToggleBot() {
    if (!selectedPhone) return
    try {
      await toggleBot(selectedPhone)
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
      {/* Left column */}
      <ConversationList
        conversations={conversations}
        selectedPhone={selectedPhone}
        onSelectPhone={setSelectedPhone}
      />

      {/* Right column */}
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

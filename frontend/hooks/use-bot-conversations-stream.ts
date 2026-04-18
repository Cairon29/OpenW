"use client"

import { useState, useEffect, useRef } from "react"
import type { BotConversation } from "@/lib/api"

interface UseStreamResult {
  conversations: BotConversation[]
  isConnected: boolean
}

export function useBotConversationsStream(): UseStreamResult {
  const [conversations, setConversations] = useState<BotConversation[]>([])
  const [isConnected, setIsConnected] = useState(false)
  const lastSeqRef = useRef<number>(-1)

  useEffect(() => {
    const es = new EventSource("/api/v1/chat/bot/stream")

    es.addEventListener("snapshot", (e: MessageEvent) => {
      const data = JSON.parse(e.data) as { seq: number; conversations: BotConversation[] }
      lastSeqRef.current = data.seq
      setConversations(data.conversations)
      setIsConnected(true)
    })

    es.addEventListener("new_message", (e: MessageEvent) => {
      const event = JSON.parse(e.data) as {
        seq: number
        phone: string
        role: "user" | "bot"
        text: string
        time: string
      }
      if (event.seq <= lastSeqRef.current) return
      lastSeqRef.current = event.seq

      setConversations((prev) => {
        const idx = prev.findIndex((c) => c.phone === event.phone)
        const newMsg = { role: event.role, text: event.text, time: event.time }
        if (idx === -1) {
          return [
            {
              phone: event.phone,
              bot_active: true,
              last_message: event.text,
              last_time: event.time,
              messages: [newMsg],
              is_typing: event.role === "bot" ? false : undefined,
            },
            ...prev,
          ]
        }
        const updated: BotConversation = {
          ...prev[idx],
          messages: [...prev[idx].messages, newMsg],
          last_message: event.text,
          last_time: event.time,
          is_typing: event.role === "bot" ? false : prev[idx].is_typing,
        }
        const next = prev.filter((_, i) => i !== idx)
        return [updated, ...next]
      })
    })

    es.addEventListener("bot_toggle", (e: MessageEvent) => {
      const event = JSON.parse(e.data) as { seq: number; phone: string; bot_active: boolean }
      if (event.seq <= lastSeqRef.current) return
      lastSeqRef.current = event.seq

      setConversations((prev) =>
        prev.map((c) => (c.phone === event.phone ? { ...c, bot_active: event.bot_active } : c))
      )
    })

    es.addEventListener("bot_typing_start", (e: MessageEvent) => {
      const ev = JSON.parse(e.data) as { seq: number; phone: string }
      if (ev.seq <= lastSeqRef.current) return
      lastSeqRef.current = ev.seq
      setConversations((prev) =>
        prev.map((c) => (c.phone === ev.phone ? { ...c, is_typing: true } : c))
      )
    })

    es.addEventListener("bot_typing_stop", (e: MessageEvent) => {
      const ev = JSON.parse(e.data) as { seq: number; phone: string }
      if (ev.seq <= lastSeqRef.current) return
      lastSeqRef.current = ev.seq
      setConversations((prev) =>
        prev.map((c) => (c.phone === ev.phone ? { ...c, is_typing: false } : c))
      )
    })

    es.onerror = () => {
      setIsConnected(false)
    }

    return () => {
      es.close()
    }
  }, [])

  return { conversations, isConnected }
}
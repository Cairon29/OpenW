"use client"

import * as React from "react"
import { Search, Archive, Filter, MessageSquare } from "lucide-react"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/data-display/avatar"
import { Input } from "@/components/ui/forms/input"
import { Button } from "@/components/ui/forms/button"
import { ScrollArea } from "@/components/ui/layout/scroll-area"
import { Badge } from "@/components/ui/data-display/badge"
import { type BotConversation } from "@/lib/api"
import { formatTime, getInitials } from "./utils"

interface ConversationListProps {
  conversations: BotConversation[]
  selectedPhone: string | null
  onSelectPhone: (phone: string) => void
}

export function ConversationList({ conversations, selectedPhone, onSelectPhone }: ConversationListProps) {
  return (
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
              const badgeColor = conv.bot_active
                ? "text-blue-500 bg-blue-50 dark:bg-blue-950/50"
                : "text-orange-500 bg-orange-50 dark:bg-orange-950/50"

              return (
                <div
                  key={conv.phone}
                  onClick={() => onSelectPhone(conv.phone)}
                  className={`flex items-start gap-3 p-3 cursor-pointer hover:bg-accent transition-colors ${isActive ? "bg-accent/50 dark:bg-accent/30" : ""}`}
                >
                  <Avatar className="h-10 w-10 border-2 border-background shadow-sm mt-0.5 shrink-0">
                    {conv.profile_photo_url && <AvatarImage src={conv.profile_photo_url} alt={conv.profile_name ?? conv.phone} />}
                    <AvatarFallback className="bg-emerald-600 text-white font-medium text-sm">
                      {getInitials(conv.profile_name, conv.phone)}
                    </AvatarFallback>
                  </Avatar>
                  <div className="flex-1 space-y-1 min-w-0 pr-1">
                    <div className="flex items-center justify-between">
                      <p className="text-[13px] font-medium leading-tight truncate pr-2">
                        {conv.profile_name ?? `+${conv.phone}`}
                      </p>
                      <span className="text-[11px] text-muted-foreground whitespace-nowrap shrink-0">
                        {formatTime(conv.last_time)}
                      </span>
                    </div>
                    <div className="flex items-center justify-between gap-2 mt-0.5">
                      <p className="text-[12px] text-muted-foreground truncate">{conv.last_message}</p>
                      <span className={`text-[9px] font-bold px-1.5 py-0.5 rounded-[4px] shrink-0 ${badgeColor}`}>
                        {conv.bot_active ? "IA" : "H"}
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
  )
}

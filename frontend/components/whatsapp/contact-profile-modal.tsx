"use client"

import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog"
import { type BotConversation } from "@/lib/api"
import { getInitials, formatPhone } from "./utils"

interface ContactProfileModalProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  conversation: BotConversation | null
}

export function ContactProfileModal({ open, onOpenChange, conversation }: ContactProfileModalProps) {
  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-sm">
        <DialogHeader>
          <DialogTitle className="text-base font-semibold">Perfil del contacto</DialogTitle>
        </DialogHeader>
        <div className="flex flex-col items-center gap-4 py-4">
          <Avatar className="h-16 w-16">
            {conversation?.profile_photo_url && (
              <AvatarImage src={conversation.profile_photo_url} alt="Foto de perfil" />
            )}
            <AvatarFallback className="bg-emerald-600 text-white text-xl font-medium">
              {getInitials(conversation?.profile_name, conversation?.phone)}
            </AvatarFallback>
          </Avatar>
          <div className="flex flex-col items-center gap-1 text-center">
            {conversation?.profile_name && (
              <span className="font-semibold text-sm">{conversation.profile_name}</span>
            )}
            <span className="text-muted-foreground text-sm">
              {conversation?.phone ? formatPhone(conversation.phone) : ""}
            </span>
          </div>
        </div>
        <div className="rounded-md border border-emerald-200 dark:border-emerald-800 bg-emerald-50 dark:bg-emerald-950/30 px-4 py-3">
          <p className="text-xs text-emerald-700 dark:text-emerald-300">Contacto de WhatsApp Business</p>
        </div>
      </DialogContent>
    </Dialog>
  )
}

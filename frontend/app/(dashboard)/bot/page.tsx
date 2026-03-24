import { WhatsAppView } from "@/components/whatsapp/whatsapp-view"

export default function BotPage() {
  return (
    <div className="h-[calc(100vh-104px)] overflow-hidden rounded-md border border-border bg-background shadow-sm">
      <WhatsAppView />
    </div>
  )
}

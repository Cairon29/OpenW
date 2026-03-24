import { SidebarProvider, SidebarInset, SidebarTrigger } from "@/components/ui/sidebar"
import { AppSidebar } from "@/components/dashboard/app-sidebar"
import { Separator } from "@/components/ui/separator"
import { Button } from "@/components/ui/button"
import { Avatar, AvatarFallback } from "@/components/ui/avatar"
import { LogOut } from "lucide-react"
import Link from "next/link"

export default function DashboardLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return (
    <SidebarProvider>
      <AppSidebar />
      <SidebarInset>
        <header className="flex h-14 shrink-0 items-center justify-between gap-2 border-b border-border px-4 shadow-sm bg-background">
          <div className="flex items-center gap-2">
            <SidebarTrigger className="-ml-1" />
            <Separator orientation="vertical" className="mr-2 h-4" />
            <span className="text-[13px] font-medium text-muted-foreground hidden md:inline-block">
              Panel de Control de Vulnerabilidades
            </span>
          </div>

          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2.5">
              <div className="hidden md:flex flex-col items-end text-sm">
                <span className="font-semibold text-[13px] leading-tight text-foreground">Admin</span>
                <span className="text-[11px] text-muted-foreground leading-tight">admin@vulntracker.com</span>
              </div>
              <Avatar className="h-8 w-8 rounded-full border border-border/50">
                <AvatarFallback className="bg-[#fa8200]/20 text-[#fa8200] text-xs font-bold">
                  A
                </AvatarFallback>
              </Avatar>
            </div>
            
            <Separator orientation="vertical" className="h-[20px]" />

            <Button variant="ghost" size="icon" className="text-muted-foreground hover:text-foreground h-8 w-8" asChild>
              <Link href="/login">
                <LogOut className="h-4 w-4" />
                <span className="sr-only">Cerrar sesión</span>
              </Link>
            </Button>
          </div>
        </header>
        <main className="flex-1 overflow-auto p-4 md:p-6 bg-[#f8f9fa] dark:bg-background">{children}</main>
      </SidebarInset>
    </SidebarProvider>
  )
}

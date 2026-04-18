import { SidebarProvider, SidebarInset } from "@/components/ui/layout/sidebar"
import { AppSidebar } from "@/components/dashboard/app-sidebar"
import { DashboardHeader } from "@/components/dashboard/dashboard-header"

export default function DashboardLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return (
    <SidebarProvider>
      <AppSidebar />
      <SidebarInset>
        <DashboardHeader />
        <main className="flex-1 overflow-auto min-w-0 p-4 md:p-6 bg-[#f8f9fa] dark:bg-background">
          {children}
        </main>
      </SidebarInset>
    </SidebarProvider>
  )
}
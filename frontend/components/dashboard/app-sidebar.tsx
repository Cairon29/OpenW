"use client"

import Link from "next/link"
import { usePathname } from "next/navigation"
import {
  LayoutDashboard,
  AlertTriangle,
  FolderOpen,
  Settings,
  MessageSquare,
  Shield,
} from "lucide-react"
import {
  Sidebar,
  SidebarContent,
  SidebarGroup,
  SidebarGroupContent,
  SidebarGroupLabel,
  SidebarHeader,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  SidebarFooter,
} from "@/components/ui/layout/sidebar"

import { ThemeToggle } from "@/components/ui/utility/theme-toggle"

const navigationItems = [
  {
    title: "Dashboard",
    href: "/",

  },
  {
    title: "Casos",
    href: "/cases",

  },
  {
    title: "Categorías",
    href: "/categories",

  },
]

const secondaryItems = [
  {
    title: "WhatsApp Bot",
    href: "/bot",

  },
  {
    title: "Configuración",
    href: "/settings",

  },
]


const TerceroItems = [
  {
    title: "Reportes",
    href: "/reports",

  },

]


export function AppSidebar() {
  const pathname = usePathname()

  return (
    <Sidebar className="border-r border-sidebar-border bg-sidebar text-sidebar-foreground">
      <SidebarHeader className="border-b border-sidebar-border px-6 py-4">
        <div className="flex items-center justify-between">
          <Link href="/" className="flex items-center gap-1 group">
            <div className="flex flex-col text-white">
              <div className="flex items-baseline gap-0">
                <span className="text-2xl font-serif font-light opacity-90">{`{`}</span>
                <span
                  className="text-xl font-bold tracking-tight"
                  style={{ fontFamily: "'Times New Roman', Times, serif" }}
                >
                  fiduprevisora
                </span>
                <span className="text-2xl font-serif font-light opacity-90">{`)`}</span>
              </div>
              <span className="text-[10px] uppercase tracking-[0.2em] opacity-60 -mt-1 ml-1">
                Security Dashboard
              </span>
            </div>
          </Link>
          <ThemeToggle />
        </div>
      </SidebarHeader>

      <SidebarContent>
        <SidebarGroup>
          <SidebarGroupLabel className="text-m uppercase tracking-wider text-[#fab568] font-semibold font-color-white">
            Principal
          </SidebarGroupLabel>
          <SidebarGroupContent>
            <SidebarMenu>
              {navigationItems.map((item) => (
                <SidebarMenuItem key={item.href}>
                  <SidebarMenuButton
                    asChild
                    isActive={pathname === item.href}
                    className="transition-colors border border-transparent dark:hover:bg-[#fab568]/15 dark:hover:border-[#fab568]/40"
                  >
                    <Link href={item.href}>

                      <span>{item.title}</span>
                    </Link>
                  </SidebarMenuButton>
                </SidebarMenuItem>
              ))}
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>

        <SidebarGroup>
          <SidebarGroupLabel className="text-xs uppercase tracking-wider text-[#fab568] font-semibold">
            Configuración
          </SidebarGroupLabel>
          <SidebarGroupContent>
            <SidebarMenu>
              {secondaryItems.map((item) => (
                <SidebarMenuItem key={item.href}>
                  <SidebarMenuButton
                    asChild
                    isActive={pathname === item.href}
                    className="transition-colors border border-transparent dark:hover:bg-[#fab568]/15 dark:hover:border-[#fab568]/40"
                  >
                    <Link href={item.href}>

                      <span>{item.title}</span>
                    </Link>
                  </SidebarMenuButton>
                </SidebarMenuItem>
              ))}
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>

        <SidebarGroup>
          <SidebarGroupLabel className="text-xs uppercase tracking-wider text-[#fab568] font-semibold">
            Panel de administracion
          </SidebarGroupLabel>
          <SidebarGroupContent>

          </SidebarGroupContent>
          <SidebarGroupContent>
            <SidebarMenu>
              {TerceroItems.map((item) => (
                <SidebarMenuItem key={item.href}>
                  <SidebarMenuButton
                    asChild
                    isActive={pathname === item.href}
                    className="transition-colors border border-transparent dark:hover:bg-[#fab568]/15 dark:hover:border-[#fab568]/40"
                  >
                    <Link href={item.href}>

                      <span>{item.title}</span>
                    </Link>
                  </SidebarMenuButton>
                </SidebarMenuItem>
              ))}
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>
      </SidebarContent>

    </Sidebar>
  )
}
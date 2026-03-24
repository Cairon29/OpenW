"use client"

import * as React from "react"
import { Search, Archive, Filter, Check, MoreVertical, Paperclip, Send, Sparkles, User, Settings2, BarChart2 } from "lucide-react"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Switch } from "@/components/ui/switch"
import { Badge } from "@/components/ui/badge"

const contacts = [
  { id: 1, name: "Erik Manuel Taveras", lastMessage: "Los horarios disponibles para la demo son m...", time: "ahora", initials: "E", color: "bg-emerald-600", active: true, badge: "IA", badgeColor: "text-blue-500 bg-blue-50 dark:bg-blue-950/50" },
  { id: 2, name: "Carlos", lastMessage: "Hola Carlos, te habla Erik, me gustaría saber q...", time: "00:24", initials: "C", color: "bg-emerald-600", active: false, badge: "H", badgeColor: "text-orange-500 bg-orange-50 dark:bg-orange-950/50" },
  { id: 3, name: "Jairo", lastMessage: "Hola Jairo, gracias por tu interés en TalosFlo...", time: "ayer", initials: "J", color: "bg-emerald-600", active: false, badge: "IA", badgeColor: "text-blue-500 bg-blue-50 dark:bg-blue-950/50" },
  { id: 4, name: "Yukata Yokoyama Antonio Durán", lastMessage: "¡Genial! Me alegra saber que te agrada la info...", time: "ayer", initials: "Y", color: "bg-emerald-600", active: false, badge: "IA", badgeColor: "text-blue-500 bg-blue-50 dark:bg-blue-950/50" },
  { id: 5, name: "Brian Jose Lopez Silva", lastMessage: "Con gusto. Primero, ¿me puedes contar un p...", time: "ayer", initials: "B", color: "bg-emerald-600", active: false, badge: "IA", badgeColor: "text-blue-500 bg-blue-50 dark:bg-blue-950/50" },
  { id: 6, name: "Raysa Taveras", lastMessage: "¡Hola! ¿Cómo estás? Si necesitas información...", time: "ayer", initials: "R", color: "bg-emerald-600", active: false, badge: "IA", badgeColor: "text-blue-500 bg-blue-50 dark:bg-blue-950/50" },
]

const messages = [
  { id: 1, type: "bot", text: "Perfecto, con gusto. Primero, ¿puedes decirme tu nombre completo y tu correo electrónico para agendar la cita?", time: "01:35" },
  { id: 2, type: "user", text: "Erik Manuel Taveras", time: "01:36" },
  { id: 3, type: "bot", text: "Gracias, Erik Manuel Taveras. Ahora, ¿me puedes compartir tu correo electrónico para completar la información y agendar la cita?", time: "01:36" },
  { id: 4, type: "user", text: "eriktaveras@gmail.com", time: "01:36" },
  { id: 5, type: "bot", text: "Perfecto, Erik. Ya tengo tu nombre y correo guardados. ¿Qué tipo de negocio tienes y qué necesitas automatizar? Esto me ayudará a ofrecerte la mejor solución.", time: "01:36" },
  { id: 6, type: "system", text: "Datos guardados: nombre: Erik Manuel Taveras, email: eriktaveras@gmail.com" },
  { id: 7, type: "date", text: "Hoy" },
  { id: 8, type: "user", text: "Tengo una agencia de marketing y me llegan muchos leads por la publicidad de facebook", time: "01:37" },
  { id: 9, type: "bot", text: "¡Genial, Erik! Con TalosFlow podemos ayudarte a calificar esos leads automáticamente y mejorar tu tiempo de respuesta. ¿Te gustaría agendar una demo personalizada para mostrarte cómo funciona?", time: "01:37" },
  { id: 10, type: "user", text: "Claro!", time: "01:38" },
  { id: 11, type: "bot", text: "Los horarios disponibles para la demo son mañana a las 9:00, 9:30, 10:00, y en la tarde a las 12:00, 12:30, 13:00. ¿Cuál de estos te gustaría reservar?", time: "01:38" },
]

export function WhatsAppView() {
  const [isBotOn, setIsBotOn] = React.useState(true)

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
              <Badge variant="secondary" className="px-1.5 min-w-6 justify-center text-xs">6</Badge>
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
          <div className="flex flex-col">
            {contacts.map((contact) => (
              <div
                key={contact.id}
                className={`flex items-start gap-3 p-3 cursor-pointer hover:bg-accent transition-colors ${
                  contact.active ? "bg-accent/50 dark:bg-accent/30" : ""
                }`}
              >
                <Avatar className="h-10 w-10 border-2 border-background shadow-sm mt-0.5 shrink-0">
                  <AvatarFallback className={`${contact.color} text-white font-medium text-sm`}>
                    {contact.initials}
                  </AvatarFallback>
                </Avatar>
                <div className="flex-1 space-y-1 min-w-0 pr-1">
                  <div className="flex items-center justify-between">
                    <p className="text-[13px] font-medium leading-tight truncate pr-2">{contact.name}</p>
                    <span className="text-[11px] text-muted-foreground whitespace-nowrap shrink-0">{contact.time}</span>
                  </div>
                  <div className="flex items-center justify-between gap-2 mt-0.5">
                    <p className="text-[12px] text-muted-foreground truncate">
                      <span className="opacity-70">Tu: </span>{contact.lastMessage}
                    </p>
                    <span className={`text-[9px] font-bold px-1.5 py-0.5 rounded-[4px] shrink-0 ${contact.badgeColor}`}>
                      {contact.badge}
                    </span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </ScrollArea>
      </div>

      {/* Right Area - Chat Content */}
      <div className="flex-1 flex flex-col h-full bg-[#f0f2f5] dark:bg-zinc-950/50 min-w-0 min-h-0 relative">
        {/* Chat Header */}
        <div className="h-[60px] px-3 md:px-5 border-b border-border bg-background flex items-center justify-between shrink-0 sticky top-0 z-20 shadow-sm">
          <div className="flex items-center gap-3 w-full max-w-[50%]">
            <div className="relative shrink-0">
              <Avatar className="h-9 w-9">
                <AvatarFallback className="bg-emerald-600 text-white font-medium text-sm">E</AvatarFallback>
              </Avatar>
              <div className="absolute right-0 bottom-0 w-2.5 h-2.5 bg-green-500 rounded-full border-2 border-background"></div>
            </div>
            <div className="flex flex-col justify-center min-w-0">
              <span className="font-semibold text-[13px] truncate">Erik Manuel Taveras</span>
              <div className="flex items-center gap-2 text-[11px] text-muted-foreground mt-0.5">
                <span className="truncate">Paso: inicio</span>
                <Badge variant="secondary" className="px-1 py-0 text-[10px] h-3.5 bg-blue-100 text-blue-700 dark:bg-blue-900 dark:text-blue-300 rounded-[4px] shrink-0 leading-none">
                  nuevo
                </Badge>
              </div>
            </div>
          </div>
          
          <div className="flex items-center gap-1.5 md:gap-2.5 shrink-0">
            <Badge variant="outline" className="hidden sm:flex gap-1 bg-emerald-50 dark:bg-emerald-950/30 text-emerald-600 border-emerald-200 text-xs px-2 py-0.5">
              <BarChart2 className="h-3 w-3" />
              <span>20</span>
            </Badge>
            <Button variant="ghost" size="icon" className="h-8 w-8 text-muted-foreground hidden sm:flex">
              <User className="h-4 w-4" />
            </Button>
            <Button 
              variant="outline" 
              size="sm" 
              className="bg-background h-8 text-xs px-2 md:px-3"
              onClick={() => setIsBotOn(false)}
            >
              <span className="hidden sm:inline">Intervenir</span>
              <span className="sm:hidden">Int.</span>
            </Button>
            <div className={`flex items-center gap-1.5 md:gap-2 px-2 md:px-2.5 py-1.5 rounded-md border text-xs transition-colors ${
              isBotOn 
                ? "bg-indigo-50 dark:bg-indigo-950/30 text-indigo-600 dark:text-indigo-400 border-indigo-100 dark:border-indigo-900/50" 
                : "bg-muted text-muted-foreground border-border"
            }`}>
              <span className="font-medium whitespace-nowrap">IA <span className="hidden sm:inline">{isBotOn ? "ON" : "OFF"}</span></span>
              <Switch 
                checked={isBotOn} 
                onCheckedChange={setIsBotOn}
                className="data-[state=checked]:bg-indigo-600 scale-[0.7] sm:scale-[0.8]"
              />
            </div>
          </div>
        </div>

        {/* Chat Messages */}
        <ScrollArea className="flex-1 min-h-0 w-full bg-[url('https://i.pinimg.com/736x/8c/98/99/8c98994518b575bfd8c949e91d20548b.jpg')] bg-opacity-5 dark:bg-blend-overlay dark:opacity-20 bg-cover bg-center">
          <div className="flex flex-col gap-3 w-full px-4 md:px-8 lg:px-12 py-6">
            {messages.map((msg) => {
              if (msg.type === "system" || msg.type === "date") {
                return (
                  <div key={msg.id} className="flex justify-center my-1.5 w-full">
                    <div className="bg-background/90 backdrop-blur-md border border-border text-muted-foreground text-[11px] px-3 py-1 rounded-full flex items-center gap-1.5 shadow-sm max-w-[90%] text-center leading-tight">
                      {msg.type === "system" && <Check className="h-3 w-3 text-emerald-500 shrink-0" />}
                      <span>{msg.text}</span>
                    </div>
                  </div>
                )
              }

              const isUser = msg.type === "user"
              
              return (
                <div key={msg.id} className={`flex w-full ${isUser ? 'justify-start' : 'justify-end'}`}>
                  <div className={`max-w-[85%] md:max-w-[75%] lg:max-w-[65%] rounded-2xl px-3.5 py-2 relative shadow-sm ${
                    isUser 
                      ? 'bg-background border border-border rounded-tl-sm' 
                      : 'bg-[#dcf8c6] dark:bg-emerald-900/90 text-emerald-950 dark:text-emerald-50 rounded-tr-sm border border-emerald-200/60 dark:border-emerald-800'
                  }`}>
                    {!isUser && (
                      <div className="flex items-center gap-1 mb-0.5 opacity-70">
                        <Sparkles className="h-[10px] w-[10px]" />
                        <span className="text-[9px] uppercase font-bold tracking-wider">IA</span>
                      </div>
                    )}
                    <p className="text-[14px] leading-relaxed whitespace-pre-wrap break-words">{msg.text}</p>
                    <div className={`text-[10px] mt-0.5 text-right ${isUser ? 'text-muted-foreground' : 'text-emerald-700/70 dark:text-emerald-400/70'}`}>
                      {msg.time}
                    </div>
                  </div>
                </div>
              )
            })}
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
                onClick={() => setIsBotOn(false)}
              >
                Responder manualmente
              </Button>
            </div>
          ) : (
            <div className="flex items-end gap-2 relative w-full">
              <div className="relative flex-1 min-w-0">
                <Input 
                  className="min-h-[44px] text-[14px] w-full rounded-[22px] pr-10 pl-4 py-2.5 bg-muted/50 border-transparent hover:border-border focus-visible:ring-1 focus-visible:ring-emerald-500 shadow-none transition-all"
                  placeholder="Escribe un mensaje manual..."
                />
                <Button 
                  variant="ghost" 
                  size="icon" 
                  className="absolute right-1 top-1/2 -translate-y-1/2 h-8 w-8 text-muted-foreground hover:text-foreground"
                >
                  <Paperclip className="h-4 w-4" />
                </Button>
              </div>
              <Button className="h-[44px] w-[44px] rounded-full shrink-0 bg-emerald-600 hover:bg-emerald-700 text-white shadow-sm transition-transform active:scale-95">
                <Send className="h-4 w-4 ml-0.5" />
              </Button>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

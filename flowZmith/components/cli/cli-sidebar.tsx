"use client"

import * as React from "react"
import { 
  FileCode, 
  Rocket, 
  Search, 
  Upload, 
  FolderOpen, 
  Globe, 
  History, 
  Activity, 
  Sparkles, 
  FolderPlus, 
  List, 
  Zap, 
  MessageSquare,
  ChevronRight,
  Settings,
  Wand2,
  Info,
  Compass
} from "lucide-react"
import { cn } from "@/lib/utils"
import { Button } from "@/components/ui/button"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Badge } from "@/components/ui/badge"
import type { CLICommand } from "@/lib/cli-commands"
import { getAllCommands, getCommandsByCategory, getAllCategories } from "@/lib/cli-commands"

const iconMap = {
  FileCode,
  Rocket,
  Search,
  Upload,
  FolderOpen,
  Globe,
  History,
  Activity,
  Sparkles,
  FolderPlus,
  List,
  Zap,
  MessageSquare,
  Settings,
  Wand2,
  Info,
  Compass,
}

interface CLISidebarProps {
  onCommandSelect: (command: CLICommand) => void
  selectedCommand?: CLICommand | null
  className?: string
}

export function CLISidebar({ onCommandSelect, selectedCommand, className }: CLISidebarProps) {
  const [expandedCategories, setExpandedCategories] = React.useState<Set<string>>(
    new Set(["contract", "deployment", "flow"])
  )

  const categories = getAllCategories()
  const allCommands = getAllCommands()

  const toggleCategory = (categoryId: string) => {
    setExpandedCategories(prev => {
      const next = new Set(prev)
      if (next.has(categoryId)) {
        next.delete(categoryId)
      } else {
        next.add(categoryId)
      }
      return next
    })
  }

  return (
    <div className={cn("flex flex-col h-full bg-background", className)}>
      <div className="p-4 border-b-2 border-foreground bg-muted/5">
        <h2 className="text-xl font-black tracking-tighter uppercase">FLOWZMITH_CLI</h2>
        <div className="flex items-center gap-2 mt-1">
          <div className="h-2 w-2 bg-accent animate-pulse" />
          <p className="text-[10px] font-bold text-foreground/50 uppercase tracking-widest">COMMAND_SELECTOR_ACTIVE</p>
        </div>
      </div>

      <ScrollArea className="flex-1">
        <div className="p-2 space-y-2 mt-2">
          {categories.map(category => {
            const commands = getCommandsByCategory(category.id)
            const isExpanded = expandedCategories.has(category.id)

            return (
              <div key={category.id} className="space-y-1">
                <Button
                  variant="ghost"
                  className={cn(
                    "w-full justify-between h-10 px-3 rounded-none border-2 border-transparent transition-all",
                    isExpanded && "border-foreground bg-muted/10"
                  )}
                  onClick={() => toggleCategory(category.id)}
                >
                  <div className="flex items-center gap-2">
                    <div className={cn("w-3 h-3 border border-foreground", category.color)} />
                    <span className="font-black text-[10px] uppercase tracking-widest">{category.label}</span>
                  </div>
                  <ChevronRight
                    className={cn(
                      "h-4 w-4 transition-transform",
                      isExpanded && "rotate-90"
                    )}
                  />
                </Button>

                {isExpanded && (
                  <div className="ml-4 space-y-1 mt-1 border-l-2 border-foreground/20 pl-2">
                    {commands.map(command => {
                      const Icon = iconMap[command.icon as keyof typeof iconMap] || FileCode
                      const isSelected = selectedCommand?.id === command.id

                      return (
                        <Button
                          key={command.id}
                          variant="ghost"
                          className={cn(
                            "w-full justify-start text-left h-auto py-3 rounded-none border-2 border-transparent transition-all",
                            isSelected ? "border-foreground bg-accent text-black" : "hover:bg-muted/10"
                          )}
                          onClick={() => onCommandSelect(command)}
                        >
                          <div className="flex items-start gap-3 w-full">
                            <Icon className={cn("h-4 w-4 mt-0.5 flex-shrink-0", isSelected ? "text-black" : "text-accent")} />
                            <div className="flex-1 min-w-0">
                              <div className={cn("font-black text-[10px] uppercase tracking-tighter", isSelected ? "text-black" : "text-foreground")}>{command.name}</div>
                              <div className={cn("text-[9px] font-bold mt-1 line-clamp-1 uppercase", isSelected ? "text-black/70" : "text-foreground/50")}>
                                {command.description}
                              </div>
                            </div>
                          </div>
                        </Button>
                      )
                    })}
                  </div>
                )}
              </div>
            )
          })}
        </div>
      </ScrollArea>

      <div className="p-4 border-t-2 border-foreground bg-black text-white">
        <div className="text-[10px] font-black uppercase tracking-widest space-y-2">
          <div className="flex items-center justify-between">
            <span className="opacity-50 text-accent">VERSION</span>
            <span className="text-white">1.2.0_BETA</span>
          </div>
          <div className="flex items-center justify-between">
            <span className="opacity-50 text-accent">CMDS_LOADED</span>
            <span className="text-white">{allCommands.length}</span>
          </div>
        </div>
      </div>
    </div>
  )
}
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
    <div className={cn("flex flex-col h-full border-r bg-background", className)}>
      <div className="p-4 border-b">
        <h2 className="text-lg font-semibold">Flowzmith CLI</h2>
        <p className="text-sm text-muted-foreground">Select a command to execute</p>
      </div>

      <ScrollArea className="flex-1">
        <div className="p-2 space-y-1">
          {categories.map(category => {
            const commands = getCommandsByCategory(category.id)
            const isExpanded = expandedCategories.has(category.id)

            return (
              <div key={category.id} className="space-y-1">
                <Button
                  variant="ghost"
                  className="w-full justify-between"
                  onClick={() => toggleCategory(category.id)}
                >
                  <div className="flex items-center gap-2">
                    <div className={cn("w-2 h-2 rounded-full", category.color)} />
                    <span className="font-medium">{category.label}</span>
                    <Badge variant="secondary" className="ml-auto">
                      {commands.length}
                    </Badge>
                  </div>
                  <ChevronRight
                    className={cn(
                      "h-4 w-4 transition-transform",
                      isExpanded && "rotate-90"
                    )}
                  />
                </Button>

                {isExpanded && (
                  <div className="ml-4 space-y-1">
                    {commands.map(command => {
                      const Icon = iconMap[command.icon as keyof typeof iconMap] || FileCode
                      const isSelected = selectedCommand?.id === command.id

                      return (
                        <Button
                          key={command.id}
                          variant={isSelected ? "secondary" : "ghost"}
                          className={cn(
                            "w-full justify-start text-left h-auto py-2",
                            isSelected && "bg-accent"
                          )}
                          onClick={() => onCommandSelect(command)}
                        >
                          <div className="flex items-start gap-2 w-full">
                            <Icon className="h-4 w-4 mt-0.5 flex-shrink-0" />
                            <div className="flex-1 min-w-0">
                              <div className="font-medium text-sm">{command.name}</div>
                              <div className="text-xs text-muted-foreground line-clamp-2">
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

      <div className="p-4 border-t">
        <div className="text-xs text-muted-foreground">
          <div className="flex items-center justify-between mb-1">
            <span>Version</span>
            <span className="font-mono">1.0.0</span>
          </div>
          <div className="flex items-center justify-between">
            <span>Commands</span>
            <span className="font-mono">{allCommands.length}</span>
          </div>
        </div>
      </div>
    </div>
  )
}

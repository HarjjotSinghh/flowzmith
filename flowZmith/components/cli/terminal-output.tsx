"use client"

import * as React from "react"
import { cn } from "@/lib/utils"
import { Terminal, X } from "lucide-react"
import { Button } from "@/components/ui/button"

interface LogEntry {
  timestamp: Date
  message: string
  type: "info" | "error" | "success" | "warning" | "command"
}

interface TerminalOutputProps {
  logs: LogEntry[]
  isStreaming: boolean
  onClear?: () => void
  className?: string
}

export function TerminalOutput({ logs, isStreaming, onClear, className }: TerminalOutputProps) {
  const scrollRef = React.useRef<HTMLDivElement>(null)
  const [autoScroll, setAutoScroll] = React.useState(true)

  // Auto-scroll to bottom when new logs arrive
  React.useEffect(() => {
    if (autoScroll && scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight
    }
  }, [logs, autoScroll])

  const formatTime = (date: Date) => {
    return date.toLocaleTimeString('en-US', { 
      hour12: false, 
      hour: '2-digit', 
      minute: '2-digit', 
      second: '2-digit',
      fractionalSecondDigits: 3
    })
  }

  const getLogColor = (type: LogEntry["type"]) => {
    switch (type) {
      case "error":
        return "text-destructive"
      case "success":
        return "text-primary"
      case "warning":
        return "text-foreground/80"
      case "command":
        return "text-foreground/80"
      default:
        return "text-foreground"
    }
  }

  const getLogPrefix = (type: LogEntry["type"]) => {
    switch (type) {
      case "error":
        return "❌"
      case "success":
        return "✅"
      case "warning":
        return "⚠️"
      case "command":
        return "▶"
      default:
        return "ℹ️"
    }
  }

  return (
    <div className={cn("flex flex-col h-full max-h-[500px] bg-card/90 rounded-lg border border-border", className)}>
      {/* Terminal Header */}
      <div className="flex items-center justify-between px-4 py-2 bg-card/95 border-b border-border rounded-t-lg">
        <div className="flex items-center gap-2">
          <Terminal className="h-4 w-4 text-primary" />
          <span className="text-sm font-mono text-foreground">Terminal Output</span>
          {isStreaming && (
            <span className="flex items-center gap-1 text-xs text-primary">
              <span className="animate-pulse">●</span>
              Streaming...
            </span>
          )}
        </div>
        <div className="flex items-center gap-2">
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setAutoScroll(!autoScroll)}
            className="h-6 px-2 text-xs"
          >
            {autoScroll ? "Auto-scroll: ON" : "Auto-scroll: OFF"}
          </Button>
          {onClear && (
            <Button
              variant="ghost"
              size="sm"
              onClick={onClear}
              className="h-6 px-2"
            >
              <X className="h-3 w-3" />
            </Button>
          )}
        </div>
      </div>

      {/* Terminal Content */}
      <div className="flex-1 p-4 overflow-y-auto" ref={scrollRef}>
        {logs.length === 0 ? (
          <div className="flex items-center justify-center h-full text-foreground/80">
            <div className="text-center">
              <Terminal className="h-12 w-12 mx-auto mb-2 opacity-50" />
              <p className="text-sm">No output yet</p>
              <p className="text-xs mt-1">Execute a command to see output</p>
            </div>
          </div>
        ) : (
          <div className="font-mono text-sm space-y-1 oveflow-y-auto">
            {logs.map((log, idx) => (
              <div key={idx} className="flex gap-3 hover:bg-card/95/50 px-2 py-1 rounded">
                <span className="text-foreground/80 text-xs flex-shrink-0 select-none">
                  {formatTime(log.timestamp)}
                </span>
                <span className="flex-shrink-0 select-none">
                  {getLogPrefix(log.type)}
                </span>
                <span className={cn("flex-1 break-all", getLogColor(log.type))}>
                  {log.message}
                </span>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Terminal Footer */}
      <div className="px-4 py-2 bg-card/95 border-t border-border rounded-b-lg">
        <div className="flex items-center justify-between text-xs text-foreground/80">
          <span>{logs.length} lines</span>
          {isStreaming && (
            <span className="text-primary">Receiving data...</span>
          )}
        </div>
      </div>
    </div>
  )
}

// Hook to manage terminal logs
export function useTerminalLogs() {
  const [logs, setLogs] = React.useState<LogEntry[]>([])
  const [isStreaming, setIsStreaming] = React.useState(false)

  const addLog = React.useCallback((message: string, type: LogEntry["type"] = "info") => {
    setLogs(prev => [...prev, { timestamp: new Date(), message, type }])
  }, [])

  const clearLogs = React.useCallback(() => {
    setLogs([])
  }, [])

  const startStreaming = React.useCallback(() => {
    setIsStreaming(true)
  }, [])

  const stopStreaming = React.useCallback(() => {
    setIsStreaming(false)
  }, [])

  return {
    logs,
    isStreaming,
    addLog,
    clearLogs,
    startStreaming,
    stopStreaming,
  }
}

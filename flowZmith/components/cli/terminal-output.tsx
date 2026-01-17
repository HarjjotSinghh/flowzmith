"use client"

import * as React from "react"
import { cn } from "@/lib/utils"
import { Terminal, X, ChevronRight, Activity } from "lucide-react"
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
        return "text-red-500"
      case "success":
        return "text-accent"
      case "warning":
        return "text-accent/70"
      case "command":
        return "text-white"
      default:
        return "text-foreground/80"
    }
  }

  const getLogPrefix = (type: LogEntry["type"]) => {
    switch (type) {
      case "error":
        return "[ERR]"
      case "success":
        return "[OK ]"
      case "warning":
        return "[WRN]"
      case "command":
        return "[CMD]"
      default:
        return "[INF]"
    }
  }

  return (
    <div className={cn("flex flex-col h-full bg-black border-2 border-foreground relative overflow-hidden", className)}>
      {/* Terminal Header */}
      <div className="flex items-center justify-between px-4 py-3 bg-accent border-b-2 border-foreground">
        <div className="flex items-center gap-3">
          <Terminal className="h-5 w-5 text-black" />
          <span className="text-xs font-black text-black uppercase tracking-widest">TERMINAL_OUTPUT_V1.2</span>
          {isStreaming && (
            <div className="flex items-center gap-2 px-2 py-0.5 bg-black text-accent text-[8px] font-black uppercase animate-pulse">
              <Activity className="h-3 w-3" />
              STREAMING_DATA
            </div>
          )}
        </div>
        <div className="flex items-center gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={() => setAutoScroll(!autoScroll)}
            className={`h-8 px-3 text-[10px] font-black uppercase border-2 border-black bg-transparent hover:bg-black hover:text-accent transition-colors ${autoScroll ? 'text-black' : 'text-black/40'}`}
          >
            SCROLL_{autoScroll ? "ON" : "OFF"}
          </Button>
          {onClear && (
            <Button
              variant="outline"
              size="sm"
              onClick={onClear}
              className="h-8 px-2 border-2 border-black bg-transparent text-black hover:bg-black hover:text-accent"
            >
              <X className="h-4 w-4" />
            </Button>
          )}
        </div>
      </div>

      {/* Terminal Content */}
      <div className="flex-1 p-6 overflow-y-auto font-mono custom-scrollbar" ref={scrollRef}>
        {logs.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full gap-4 opacity-30">
            <Terminal className="h-16 w-16 text-accent" />
            <div className="text-center space-y-1">
              <p className="font-black uppercase text-xs tracking-[0.3em]">WAITING_FOR_COMMAND</p>
              <p className="text-[10px] font-bold uppercase">EXECUTION_QUEUE_EMPTY</p>
            </div>
          </div>
        ) : (
          <div className="space-y-2">
            {logs.map((log, idx) => (
              <div key={idx} className="flex gap-4 group transition-colors px-2 py-1 hover:bg-white/5">
                <span className="text-foreground/30 text-[10px] font-bold flex-shrink-0 select-none pt-0.5">
                  {formatTime(log.timestamp)}
                </span>
                <span className={cn("flex-shrink-0 select-none text-[10px] font-black", getLogColor(log.type))}>
                  {getLogPrefix(log.type)}
                </span>
                <span className={cn("flex-1 text-[11px] font-bold leading-relaxed uppercase tracking-tight", getLogColor(log.type))}>
                  {log.message}
                </span>
              </div>
            ))}
            {isStreaming && (
              <div className="flex gap-4 px-2 py-1">
                <span className="text-foreground/30 text-[10px] font-bold flex-shrink-0">
                  {formatTime(new Date())}
                </span>
                <span className="text-accent text-[10px] font-black select-none">
                  [CMD]
                </span>
                <span className="text-accent text-[11px] font-bold animate-pulse">
                  _
                </span>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Terminal Footer */}
      <div className="px-4 py-2 border-t-2 border-foreground bg-black/50 text-[10px] font-black uppercase tracking-widest flex justify-between">
        <div className="flex gap-4">
          <span>LINES: {logs.length.toString().padStart(4, '0')}</span>
          <span>BUFFER: 100%</span>
        </div>
        <span className="text-accent">ENCRYPTED_VT100</span>
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
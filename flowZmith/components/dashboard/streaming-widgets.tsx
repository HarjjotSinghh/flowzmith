"use client"

import { useState, useEffect, useRef } from "react"
import { motion, AnimatePresence } from "framer-motion"
import { 
  Zap, 
  Code, 
  Activity, 
  TrendingUp, 
  Clock, 
  CheckCircle, 
  AlertCircle,
  Loader2,
  Sparkles,
  BarChart3,
  Users,
  FileText,
  Cpu,
  Wifi,
  WifiOff
} from "lucide-react"

interface StreamingData {
  id: string
  type: "generation" | "analysis" | "deployment" | "activity"
  status: "pending" | "processing" | "completed" | "error"
  progress: number
  title: string
  description: string
  timestamp: Date
  metadata?: Record<string, any>
}

interface WidgetProps {
  title: string
  icon: React.ReactNode
  children: React.ReactNode
  className?: string
  isLive?: boolean
}

function StreamingWidget({ title, icon, children, className = "", isLive = false }: WidgetProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className={`relative bg-gradient-to-br from-card/60 to-card/30 backdrop-blur-sm rounded-2xl border border-border/50 p-6 shadow-xl overflow-hidden ${className}`}
    >
      {/* Live indicator */}
      {isLive && (
        <motion.div
          initial={{ scale: 0 }}
          animate={{ scale: 1 }}
          className="absolute top-4 right-4 flex items-center space-x-2 px-2 py-1 bg-green-500/10 border border-green-500/20 rounded-full"
        >
          <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
          <span className="text-xs text-green-500 font-medium">Live</span>
        </motion.div>
      )}

      {/* Header */}
      <div className="flex items-center space-x-3 mb-6">
        <motion.div
          whileHover={{ rotate: 5, scale: 1.1 }}
          className="p-2 bg-gradient-to-r from-purple-500/20 to-blue-500/20 rounded-lg"
        >
          {icon}
        </motion.div>
        <div>
          <h3 className="text-lg font-bold bg-gradient-to-r from-foreground to-foreground/70 bg-clip-text text-transparent">
            {title}
          </h3>
        </div>
      </div>

      {/* Content */}
      {children}
    </motion.div>
  )
}

function ContractGenerationWidget() {
  const [activeGenerations, setActiveGenerations] = useState<StreamingData[]>([])
  const [completedToday, setCompletedToday] = useState(0)
  const [isConnected, setIsConnected] = useState(true)

  useEffect(() => {
    // Simulate real-time contract generation updates
    const interval = setInterval(() => {
      if (Math.random() > 0.8) { // 20% chance every 3 seconds
        const contractTypes = [
          "ERC-20 Token",
          "ERC-721 NFT",
          "DeFi Protocol",
          "DAO Governance",
          "Multi-sig Wallet",
          "Staking Contract"
        ]
        
        const newGeneration: StreamingData = {
          id: `gen-${Date.now()}`,
          type: "generation",
          status: "processing",
          progress: 0,
          title: contractTypes[Math.floor(Math.random() * contractTypes.length)],
          description: "Generating smart contract...",
          timestamp: new Date()
        }

        setActiveGenerations(prev => [...prev, newGeneration])

        // Simulate progress
        let progress = 0
        const progressInterval = setInterval(() => {
          progress += Math.random() * 20 + 5
          if (progress >= 100) {
            progress = 100
            clearInterval(progressInterval)
            
            setTimeout(() => {
              setActiveGenerations(prev => prev.filter(g => g.id !== newGeneration.id))
              setCompletedToday(prev => prev + 1)
            }, 1000)
          }
          
          setActiveGenerations(prev => 
            prev.map(g => 
              g.id === newGeneration.id 
                ? { ...g, progress, status: progress === 100 ? "completed" : "processing" }
                : g
            )
          )
        }, 200)
      }
    }, 3000)

    return () => clearInterval(interval)
  }, [])

  return (
    <StreamingWidget
      title="Contract Generation"
      icon={<Code className="h-5 w-5 text-purple-500" />}
      isLive={activeGenerations.length > 0}
    >
      <div className="space-y-4">
        {/* Stats */}
        <div className="grid grid-cols-2 gap-4">
          <div className="bg-card/30 rounded-xl p-4 border border-border/30">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm text-muted-foreground">Active</span>
              <motion.div
                animate={{ rotate: activeGenerations.length > 0 ? 360 : 0 }}
                transition={{ duration: 2, repeat: activeGenerations.length > 0 ? Infinity : 0, ease: "linear" }}
              >
                <Loader2 className={`h-4 w-4 ${activeGenerations.length > 0 ? 'text-purple-500' : 'text-muted-foreground'}`} />
              </motion.div>
            </div>
            <div className="text-2xl font-bold text-foreground">{activeGenerations.length}</div>
          </div>
          
          <div className="bg-card/30 rounded-xl p-4 border border-border/30">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm text-muted-foreground">Today</span>
              <CheckCircle className="h-4 w-4 text-green-500" />
            </div>
            <motion.div 
              key={completedToday}
              initial={{ scale: 1.2, color: "#10b981" }}
              animate={{ scale: 1, color: "inherit" }}
              className="text-2xl font-bold text-foreground"
            >
              {completedToday}
            </motion.div>
          </div>
        </div>

        {/* Active generations */}
        <div className="space-y-3 max-h-48 overflow-y-auto custom-scrollbar">
          <AnimatePresence>
            {activeGenerations.map((generation) => (
              <motion.div
                key={generation.id}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: 20 }}
                className="bg-card/20 rounded-lg p-3 border border-border/20"
              >
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-medium text-foreground">{generation.title}</span>
                  <span className="text-xs text-purple-500 font-medium">{Math.round(generation.progress)}%</span>
                </div>
                
                <div className="w-full h-1.5 bg-muted rounded-full overflow-hidden mb-2">
                  <motion.div
                    className="h-full bg-gradient-to-r from-purple-500 to-blue-500"
                    initial={{ width: 0 }}
                    animate={{ width: `${generation.progress}%` }}
                    transition={{ duration: 0.3 }}
                  />
                </div>
                
                <p className="text-xs text-muted-foreground">{generation.description}</p>
              </motion.div>
            ))}
          </AnimatePresence>
          
          {activeGenerations.length === 0 && (
            <div className="text-center py-6">
              <Code className="h-8 w-8 text-muted-foreground mx-auto mb-2" />
              <p className="text-sm text-muted-foreground">No active generations</p>
            </div>
          )}
        </div>
      </div>
    </StreamingWidget>
  )
}

function SystemStatusWidget() {
  const [cpuUsage, setCpuUsage] = useState(0)
  const [memoryUsage, setMemoryUsage] = useState(0)
  const [apiLatency, setApiLatency] = useState(0)
  const [isOnline, setIsOnline] = useState(true)

  useEffect(() => {
    const interval = setInterval(() => {
      setCpuUsage(Math.random() * 100)
      setMemoryUsage(Math.random() * 100)
      setApiLatency(Math.random() * 200 + 50)
      setIsOnline(Math.random() > 0.1) // 90% uptime
    }, 2000)

    return () => clearInterval(interval)
  }, [])

  const getStatusColor = (value: number, thresholds: [number, number]) => {
    if (value < thresholds[0]) return "text-green-500"
    if (value < thresholds[1]) return "text-yellow-500"
    return "text-red-500"
  }

  const getStatusBg = (value: number, thresholds: [number, number]) => {
    if (value < thresholds[0]) return "from-green-500/20 to-green-500/10"
    if (value < thresholds[1]) return "from-yellow-500/20 to-yellow-500/10"
    return "from-red-500/20 to-red-500/10"
  }

  return (
    <StreamingWidget
      title="System Status"
      icon={isOnline ? <Wifi className="h-5 w-5 text-green-500" /> : <WifiOff className="h-5 w-5 text-red-500" />}
      isLive={isOnline}
    >
      <div className="space-y-4">
        {/* Connection Status */}
        <div className={`flex items-center justify-between p-3 rounded-lg bg-gradient-to-r ${
          isOnline ? 'from-green-500/10 to-green-500/5 border-green-500/20' : 'from-red-500/10 to-red-500/5 border-red-500/20'
        } border`}>
          <div className="flex items-center space-x-2">
            <div className={`w-2 h-2 rounded-full ${isOnline ? 'bg-green-500 animate-pulse' : 'bg-red-500'}`} />
            <span className="text-sm font-medium">{isOnline ? 'Online' : 'Offline'}</span>
          </div>
          <span className={`text-xs ${isOnline ? 'text-green-500' : 'text-red-500'}`}>
            {isOnline ? 'All systems operational' : 'Connection lost'}
          </span>
        </div>

        {/* Metrics */}
        <div className="grid grid-cols-1 gap-3">
          {/* CPU Usage */}
          <div className="bg-card/20 rounded-lg p-3 border border-border/20">
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center space-x-2">
                <Cpu className="h-4 w-4 text-blue-500" />
                <span className="text-sm text-muted-foreground">CPU</span>
              </div>
              <span className={`text-sm font-medium ${getStatusColor(cpuUsage, [60, 80])}`}>
                {Math.round(cpuUsage)}%
              </span>
            </div>
            <div className="w-full h-1.5 bg-muted rounded-full overflow-hidden">
              <motion.div
                className={`h-full bg-gradient-to-r ${getStatusBg(cpuUsage, [60, 80])}`}
                initial={{ width: 0 }}
                animate={{ width: `${cpuUsage}%` }}
                transition={{ duration: 0.5 }}
              />
            </div>
          </div>

          {/* Memory Usage */}
          <div className="bg-card/20 rounded-lg p-3 border border-border/20">
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center space-x-2">
                <BarChart3 className="h-4 w-4 text-purple-500" />
                <span className="text-sm text-muted-foreground">Memory</span>
              </div>
              <span className={`text-sm font-medium ${getStatusColor(memoryUsage, [70, 85])}`}>
                {Math.round(memoryUsage)}%
              </span>
            </div>
            <div className="w-full h-1.5 bg-muted rounded-full overflow-hidden">
              <motion.div
                className={`h-full bg-gradient-to-r ${getStatusBg(memoryUsage, [70, 85])}`}
                initial={{ width: 0 }}
                animate={{ width: `${memoryUsage}%` }}
                transition={{ duration: 0.5 }}
              />
            </div>
          </div>

          {/* API Latency */}
          <div className="bg-card/20 rounded-lg p-3 border border-border/20">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <Clock className="h-4 w-4 text-green-500" />
                <span className="text-sm text-muted-foreground">API Latency</span>
              </div>
              <span className={`text-sm font-medium ${getStatusColor(apiLatency, [100, 150])}`}>
                {Math.round(apiLatency)}ms
              </span>
            </div>
          </div>
        </div>
      </div>
    </StreamingWidget>
  )
}

function LiveMetricsWidget() {
  const [activeUsers, setActiveUsers] = useState(0)
  const [requestsPerMinute, setRequestsPerMinute] = useState(0)
  const [successRate, setSuccessRate] = useState(0)

  useEffect(() => {
    const interval = setInterval(() => {
      setActiveUsers(Math.floor(Math.random() * 50) + 10)
      setRequestsPerMinute(Math.floor(Math.random() * 100) + 20)
      setSuccessRate(Math.random() * 10 + 90) // 90-100% success rate
    }, 3000)

    return () => clearInterval(interval)
  }, [])

  return (
    <StreamingWidget
      title="Live Metrics"
      icon={<TrendingUp className="h-5 w-5 text-green-500" />}
      isLive={true}
    >
      <div className="grid grid-cols-1 gap-4">
        {/* Active Users */}
        <motion.div
          whileHover={{ scale: 1.02 }}
          className="bg-gradient-to-r from-blue-500/10 to-blue-500/5 rounded-lg p-4 border border-blue-500/20"
        >
          <div className="flex items-center justify-between mb-2">
            <div className="flex items-center space-x-2">
              <Users className="h-4 w-4 text-blue-500" />
              <span className="text-sm text-muted-foreground">Active Users</span>
            </div>
            <motion.div
              key={activeUsers}
              initial={{ scale: 1.2, color: "#3b82f6" }}
              animate={{ scale: 1, color: "inherit" }}
              className="text-lg font-bold text-foreground"
            >
              {activeUsers}
            </motion.div>
          </div>
        </motion.div>

        {/* Requests per Minute */}
        <motion.div
          whileHover={{ scale: 1.02 }}
          className="bg-gradient-to-r from-purple-500/10 to-purple-500/5 rounded-lg p-4 border border-purple-500/20"
        >
          <div className="flex items-center justify-between mb-2">
            <div className="flex items-center space-x-2">
              <Activity className="h-4 w-4 text-purple-500" />
              <span className="text-sm text-muted-foreground">Requests/min</span>
            </div>
            <motion.div
              key={requestsPerMinute}
              initial={{ scale: 1.2, color: "#8b5cf6" }}
              animate={{ scale: 1, color: "inherit" }}
              className="text-lg font-bold text-foreground"
            >
              {requestsPerMinute}
            </motion.div>
          </div>
        </motion.div>

        {/* Success Rate */}
        <motion.div
          whileHover={{ scale: 1.02 }}
          className="bg-gradient-to-r from-green-500/10 to-green-500/5 rounded-lg p-4 border border-green-500/20"
        >
          <div className="flex items-center justify-between mb-2">
            <div className="flex items-center space-x-2">
              <CheckCircle className="h-4 w-4 text-green-500" />
              <span className="text-sm text-muted-foreground">Success Rate</span>
            </div>
            <motion.div
              key={Math.round(successRate)}
              initial={{ scale: 1.2, color: "#10b981" }}
              animate={{ scale: 1, color: "inherit" }}
              className="text-lg font-bold text-foreground"
            >
              {successRate.toFixed(1)}%
            </motion.div>
          </div>
          <div className="w-full h-1.5 bg-muted rounded-full overflow-hidden">
            <motion.div
              className="h-full bg-gradient-to-r from-green-500 to-emerald-500"
              initial={{ width: 0 }}
              animate={{ width: `${successRate}%` }}
              transition={{ duration: 0.5 }}
            />
          </div>
        </motion.div>
      </div>
    </StreamingWidget>
  )
}

export function StreamingWidgets() {
  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6">
      <ContractGenerationWidget />
      <SystemStatusWidget />
      <LiveMetricsWidget />
    </div>
  )
}

export { ContractGenerationWidget, SystemStatusWidget, LiveMetricsWidget, StreamingWidget }
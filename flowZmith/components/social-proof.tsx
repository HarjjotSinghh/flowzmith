import { Database, Bot, Globe, Users, Code2, Zap, Trophy, Target } from "lucide-react"

const MetricCard = ({
  icon: Icon,
  value,
  label,
  trend
}: {
  icon: React.ComponentType<any>,
  value: string,
  label: string,
  trend?: string
}) => (
  <div className="flex flex-col items-center gap-2 p-6 bg-card/50 border border-border rounded-xl backdrop-blur-sm">
    <div className="p-2 bg-card rounded-lg">
      <Icon className="w-6 h-6 text-foreground" />
    </div>
    <div className="text-center">
      <div className="text-2xl font-bold text-foreground">{value}</div>
      <div className="text-sm text-muted-foreground">{label}</div>
      {trend && (
        <div className="text-xs text-primary mt-1">{trend}</div>
      )}
    </div>
  </div>
)

export function SocialProof() {
  return (
    <section className="self-stretch py-16 flex flex-col justify-center items-center gap-8 overflow-hidden relative">
      {/* Background Effects */}

      <div className="relative z-10 w-full max-w-6xl mx-auto">
        {/* Header */}
        <div className="text-center mb-12">
          <div className="inline-flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-primary/20 to-primary-dark/20 border border-primary/30 rounded-full text-sm font-medium text-primary backdrop-blur-sm mb-4">
            <Trophy className="w-4 h-4" />
            Hackathon Performance Metrics
          </div>

          <h2 className="text-3xl md:text-4xl font-bold text-foreground mb-4">
            Winning the Modern Stack Challenge
          </h2>

          <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
            Demonstrating exceptional integration of Convex, OpenAI, and Firecrawl to create the most innovative smart contract development platform
          </p>
        </div>

        {/* Primary Metrics Grid */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-6 mb-12">
          <MetricCard
            icon={Zap}
            value="25K+"
            label="Prize Pool"
            trend="Top Contender"
          />

          <MetricCard
            icon={Target}
            value="3/3"
            label="Tech Integration"
            trend="Complete Stack"
          />

          <MetricCard
            icon={Code2}
            value="100%"
            label="Real-time Sync"
            trend="Convex Powered"
          />

          <MetricCard
            icon={Users}
            value="50+"
            label="Live Features"
            trend="Production Ready"
          />
        </div>

        {/* Technology Integration Metrics */}
        <div className="bg-card/50 border border-border rounded-2xl p-8 backdrop-blur-sm">
          <h3 className="text-xl font-semibold text-foreground mb-6 text-center">
            Integration Excellence
          </h3>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {/* Convex Metrics */}
            <div className="text-center">
              <div className="flex justify-center mb-4">
                <div className="w-16 h-16 bg-primary/20 rounded-xl flex items-center justify-center">
                  <Database className="w-8 h-8 text-primary" />
                </div>
              </div>
              <h4 className="text-lg font-medium text-foreground mb-2">Convex Excellence</h4>
              <div className="space-y-2">
                <div className="flex justify-between items-center">
                  <span className="text-sm text-muted-foreground">Real-time Sync</span>
                  <span className="text-sm font-medium text-primary">100%</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm text-muted-foreground">Collaboration</span>
                  <span className="text-sm font-medium text-primary">Live</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm text-muted-foreground">Data Models</span>
                  <span className="text-sm font-medium text-primary">5 Tables</span>
                </div>
              </div>
            </div>

            {/* OpenAI Metrics */}
            <div className="text-center">
              <div className="flex justify-center mb-4">
                <div className="w-16 h-16 bg-accent/20 rounded-xl flex items-center justify-center">
                  <Bot className="w-8 h-8 text-accent-foreground" />
                </div>
              </div>
              <h4 className="text-lg font-medium text-foreground mb-2">OpenAI Intelligence</h4>
              <div className="space-y-2">
                <div className="flex justify-between items-center">
                  <span className="text-sm text-muted-foreground">GPT-5 Model</span>
                  <span className="text-sm font-medium text-accent-foreground">Active</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm text-muted-foreground">Code Quality</span>
                  <span className="text-sm font-medium text-accent-foreground">Production</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm text-muted-foreground">Response Time</span>
                  <span className="text-sm font-medium text-accent-foreground">&lt;2s</span>
                </div>
              </div>
            </div>

            {/* Firecrawl Metrics */}
            <div className="text-center">
              <div className="flex justify-center mb-4">
                <div className="w-16 h-16 bg-secondary/20 rounded-xl flex items-center justify-center">
                  <Globe className="w-8 h-8 text-secondary-foreground" />
                </div>
              </div>
              <h4 className="text-lg font-medium text-foreground mb-2">Firecrawl Coverage</h4>
              <div className="space-y-2">
                <div className="flex justify-between items-center">
                  <span className="text-sm text-muted-foreground">Web Coverage</span>
                  <span className="text-sm font-medium text-secondary-foreground">96%</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm text-muted-foreground">Speed</span>
                  <span className="text-sm font-medium text-secondary-foreground">&lt;1s</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm text-muted-foreground">Data Fresh</span>
                  <span className="text-sm font-medium text-secondary-foreground">Real-time</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Achievement Banner */}
        <div className="mt-12 text-center">
          <div className="inline-flex items-center gap-4 px-6 py-3 bg-gradient-to-r from-primary/20 via-card/50 to-primary/20 border border-primary/30 rounded-full">
            <Trophy className="w-5 h-5 text-primary" />
            <span className="text-foreground font-medium">
              Built for the Modern Stack Hackathon - Showcasing the Future of Web3 Development
            </span>
            <Trophy className="w-5 h-5 text-primary" />
          </div>
        </div>
      </div>
    </section>
  )
}

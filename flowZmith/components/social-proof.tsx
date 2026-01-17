import { Database, Bot, Globe, Users, Code2, Zap } from "lucide-react"

const MetricCard = ({
  icon: Icon,
  value,
  label,
  trend,
}: {
  icon: React.ComponentType<any>
  value: string
  label: string
  trend?: string
}) => (
  <div className="flex flex-col items-start gap-4 rounded-2xl border border-border/70 bg-card/80 p-6">
    <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-muted/70 text-muted-foreground">
      <Icon className="h-5 w-5" />
    </div>
    <div>
      <div className="text-2xl font-semibold text-foreground">{value}</div>
      <div className="text-sm text-muted-foreground">{label}</div>
      {trend && (
        <div className="mt-2 inline-flex items-center gap-2 text-xs font-semibold text-primary">
          <span className="h-1.5 w-1.5 rounded-full bg-primary" />
          {trend}
        </div>
      )}
    </div>
  </div>
)

export function SocialProof() {
  return (
    <section className="py-16">
      <div className="mx-auto w-full max-w-6xl px-6">
        <div className="text-center mb-12">
          <div className="inline-flex items-center gap-2 rounded-full border border-border bg-muted/70 px-4 py-2 text-xs font-semibold uppercase tracking-[0.2em] text-muted-foreground">
            Proof of momentum
          </div>
          <h2 className="mt-6 text-3xl md:text-4xl font-display font-semibold text-foreground">
            Trusted infrastructure for modern Flow teams
          </h2>
          <p className="mt-4 text-lg text-muted-foreground max-w-2xl mx-auto">
            Flowzmith integrates real-time data, AI guidance, and deployment safeguards to keep builders shipping safely.
          </p>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
          <MetricCard icon={Zap} value="25K+" label="Deployments simulated" trend="Live beta" />
          <MetricCard icon={Code2} value="100%" label="Real-time sync" trend="Convex powered" />
          <MetricCard icon={Users} value="50+" label="Teams onboarded" trend="Growing weekly" />
          <MetricCard icon={Database} value="5" label="Data pipelines" trend="Automated" />
        </div>

        <div className="mt-12 grid grid-cols-1 md:grid-cols-3 gap-6">
          {[
            {
              title: "Convex backbone",
              description: "Low-latency collaboration layers backed by live sync.",
              icon: Database,
            },
            {
              title: "OpenAI copilots",
              description: "Prompt-to-contract generation with guardrails and reviews.",
              icon: Bot,
            },
            {
              title: "Firecrawl intel",
              description: "Context ingestion from docs, audits, and changelogs.",
              icon: Globe,
            },
          ].map((item) => (
            <div key={item.title} className="rounded-2xl border border-border/70 bg-card/80 p-6">
              <div className="flex items-center gap-3">
                <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-muted/70 text-muted-foreground">
                  <item.icon className="h-5 w-5" />
                </div>
                <div className="text-sm font-semibold text-foreground">{item.title}</div>
              </div>
              <p className="mt-4 text-sm text-muted-foreground">{item.description}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}

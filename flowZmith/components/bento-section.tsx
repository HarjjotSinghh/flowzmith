import { ShieldCheck, Sparkles, Workflow, Timer, Server, Wand2 } from "lucide-react"

const features = [
  {
    title: "Prompt-to-contract",
    description: "Generate Cadence contracts with guided prompts and built-in linting.",
    icon: Wand2,
  },
  {
    title: "Realtime collaboration",
    description: "Invite teammates and edit in sync with instant updates.",
    icon: Workflow,
  },
  {
    title: "Security guardrails",
    description: "Automatic checks for common Flow vulnerabilities.",
    icon: ShieldCheck,
  },
  {
    title: "Speed runs",
    description: "Compile, simulate, and deploy in a single workspace.",
    icon: Timer,
  },
  {
    title: "Observability",
    description: "Track usage, credits, and deployment stats in one place.",
    icon: Server,
  },
  {
    title: "AI reviews",
    description: "Contextual feedback on code quality before you ship.",
    icon: Sparkles,
  },
]

export function BentoSection() {
  return (
    <section className="py-16">
      <div className="mx-auto w-full max-w-6xl px-6">
        <div className="flex flex-col gap-4 text-center">
          <div className="inline-flex items-center justify-center">
            <span className="inline-flex items-center gap-2 rounded-full border border-border bg-muted/70 px-4 py-2 text-xs font-semibold uppercase tracking-[0.2em] text-muted-foreground">
              Feature set
            </span>
          </div>
          <h2 className="text-3xl md:text-4xl font-display font-semibold text-foreground">
            Everything you need to ship on Flow
          </h2>
          <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
            A single workspace for ideation, generation, validation, and deployment with tight AI support.
          </p>
        </div>

        <div className="mt-12 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {features.map((feature) => (
            <div key={feature.title} className="group rounded-2xl border border-border/70 bg-card/80 p-6 transition-all duration-300 hover:-translate-y-1 hover:shadow-lg">
              <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-muted/70 text-muted-foreground group-hover:text-primary">
                <feature.icon className="h-6 w-6" />
              </div>
              <h3 className="mt-5 text-lg font-semibold text-foreground">
                {feature.title}
              </h3>
              <p className="mt-2 text-sm text-muted-foreground">
                {feature.description}
              </p>
              <div className="mt-4 h-1 w-10 rounded-full bg-primary/60 transition-all duration-300 group-hover:w-16" />
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}

import { Button } from "@/components/ui/button"
import Link from "next/link"
import { ArrowUpRight, Play, Terminal } from "lucide-react"

export default function LiveDemoSection() {
  return (
    <section className="py-16">
      <div className="mx-auto w-full max-w-6xl px-6">
        <div className="grid gap-10 lg:grid-cols-[1.1fr_0.9fr]">
          <div className="space-y-6">
            <div className="inline-flex items-center gap-2 rounded-full border border-border bg-muted/70 px-4 py-2 text-xs font-semibold uppercase tracking-[0.2em] text-muted-foreground">
              Live workspace
            </div>
            <h2 className="text-3xl md:text-4xl font-display font-semibold text-foreground">
              See contracts generated and deployed in one flow
            </h2>
            <p className="text-lg text-muted-foreground">
              Every prompt is captured, reviewed, and pushed to Flow with full context. Stay inside one workspace while Flowzmith handles the heavy lifting.
            </p>
            <div className="flex flex-wrap gap-3">
              <Link href="/chat">
                <Button className="rounded-full px-6">
                  Launch workspace
                  <ArrowUpRight className="ml-2 h-4 w-4" />
                </Button>
              </Link>
              <Link href="https://www.youtube.com/watch?v=LL6dfPs0COo" target="_blank">
                <Button variant="outline" className="rounded-full px-6">
                  Watch demo
                </Button>
              </Link>
            </div>
          </div>

          <div className="space-y-4">
            <div className="rounded-3xl border border-border/70 bg-card/80 p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-xs uppercase tracking-[0.2em] text-muted-foreground">Session</p>
                  <p className="text-lg font-semibold text-foreground">Flow contract generator</p>
                </div>
                <span className="inline-flex items-center gap-2 rounded-full border border-border px-3 py-1 text-xs text-muted-foreground">
                  <span className="h-1.5 w-1.5 rounded-full bg-primary" />
                  Live
                </span>
              </div>
              <div className="mt-6 space-y-3 text-sm text-muted-foreground">
                <div className="flex items-center justify-between">
                  <span>Prompt cycles</span>
                  <span className="text-foreground">12</span>
                </div>
                <div className="flex items-center justify-between">
                  <span>Average response</span>
                  <span className="text-foreground">1.6s</span>
                </div>
                <div className="flex items-center justify-between">
                  <span>Deploy success</span>
                  <span className="text-foreground">98%</span>
                </div>
              </div>
            </div>

            <div className="rounded-3xl border border-border/70 bg-card/80 p-6">
              <div className="flex items-center gap-3">
                <div className="flex h-10 w-10 items-center justify-center rounded-2xl bg-muted/70 text-muted-foreground">
                  <Terminal className="h-5 w-5" />
                </div>
                <div>
                  <p className="text-sm font-semibold text-foreground">Realtime terminal</p>
                  <p className="text-xs text-muted-foreground">Deploy, test, and ship</p>
                </div>
              </div>
              <div className="mt-4 rounded-2xl border border-border bg-muted/70 p-4 font-mono text-xs text-muted-foreground">
                <p>$ flow deploy StreamingRewards.cdc</p>
                <p className="mt-2 text-primary">? Deployment successful in 14s</p>
              </div>
            </div>

            <div className="rounded-3xl border border-border/70 bg-card/80 p-6">
              <div className="flex items-center gap-3">
                <div className="flex h-10 w-10 items-center justify-center rounded-2xl bg-muted/70 text-muted-foreground">
                  <Play className="h-5 w-5" />
                </div>
                <div>
                  <p className="text-sm font-semibold text-foreground">Workflow automation</p>
                  <p className="text-xs text-muted-foreground">Generate, review, deploy</p>
                </div>
              </div>
              <div className="mt-4 flex items-center gap-2 text-xs text-muted-foreground">
                <span className="rounded-full border border-border px-2 py-1">Generate</span>
                <span className="rounded-full border border-border px-2 py-1">Review</span>
                <span className="rounded-full border border-border px-2 py-1">Deploy</span>
                <span className="rounded-full border border-border px-2 py-1">Monitor</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}

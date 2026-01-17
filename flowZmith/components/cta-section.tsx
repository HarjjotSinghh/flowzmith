import { Button } from "@/components/ui/button"
import Link from "next/link"
import { ArrowRight } from "lucide-react"

export function CTASection() {
  return (
    <section className="py-16">
      <div className="mx-auto w-full max-w-6xl px-6">
        <div className="rounded-3xl border border-border/70 bg-card/85 p-10 md:p-14">
          <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-8">
            <div className="space-y-4">
              <div className="inline-flex items-center gap-2 rounded-full border border-border bg-muted/70 px-4 py-2 text-xs font-semibold uppercase tracking-[0.2em] text-muted-foreground">
                Ready to build
              </div>
              <h2 className="text-3xl md:text-4xl font-display font-semibold text-foreground">
                The Flowzmith workspace is ready when you are
              </h2>
              <p className="text-lg text-muted-foreground max-w-2xl">
                Spin up a new Flow contract in minutes, collaborate in real-time, and ship confidently with AI guardrails.
              </p>
            </div>
            <div className="flex flex-col sm:flex-row gap-3">
              <Link href="/login">
                <Button className="rounded-full px-6">
                  Start building
                  <ArrowRight className="ml-2 h-4 w-4" />
                </Button>
              </Link>
              <Link href="/plans">
                <Button variant="outline" className="rounded-full px-6">
                  Compare plans
                </Button>
              </Link>
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}

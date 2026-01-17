"use client"

import { useState } from "react"
import { Check } from "lucide-react"
import { Button } from "@/components/ui/button"

export function PricingSection() {
  const [isAnnual, setIsAnnual] = useState(true)

  const pricingPlans = [
    {
      name: "Free",
      monthlyPrice: "$0",
      annualPrice: "$0",
      description: "Perfect for individual builders getting started.",
      features: [
        "Real-time code suggestions",
        "Single MCP server connection",
        "Up to 2 AI coding agents",
        "Flow test deployments",
      ],
      buttonText: "Get started",
    },
    {
      name: "Pro",
      monthlyPrice: "$20",
      annualPrice: "$16",
      description: "Ideal for professional teams shipping weekly.",
      features: [
        "Enhanced real-time previews",
        "Multiple MCP server connections",
        "Up to 10 AI coding agents",
        "Collaborative team chat",
        "Priority support",
      ],
      buttonText: "Join Pro",
      popular: true,
    },
    {
      name: "Ultra",
      monthlyPrice: "$200",
      annualPrice: "$160",
      description: "Enterprise scale with dedicated support.",
      features: [
        "Unlimited MCP server clusters",
        "Unlimited AI coding agents",
        "Enterprise security & compliance",
        "SLA-backed deployments",
      ],
      buttonText: "Talk to sales",
    },
  ]

  return (
    <section className="py-16">
      <div className="mx-auto w-full max-w-6xl px-6">
        <div className="text-center">
          <h2 className="text-3xl md:text-4xl font-display font-semibold text-foreground">
            Pricing built for every developer
          </h2>
          <p className="mt-4 text-lg text-muted-foreground max-w-2xl mx-auto">
            Choose a plan that fits your workflow, from indie builders to enterprise teams.
          </p>
        </div>

        <div className="mt-8 flex items-center justify-center">
          <div className="inline-flex items-center rounded-full border border-border bg-muted/70 p-1">
            <button
              onClick={() => setIsAnnual(true)}
              className={`px-4 py-1.5 text-sm font-medium rounded-full transition-colors ${
                isAnnual ? "bg-foreground text-background" : "text-muted-foreground"
              }`}
            >
              Annual
            </button>
            <button
              onClick={() => setIsAnnual(false)}
              className={`px-4 py-1.5 text-sm font-medium rounded-full transition-colors ${
                !isAnnual ? "bg-foreground text-background" : "text-muted-foreground"
              }`}
            >
              Monthly
            </button>
          </div>
        </div>

        <div className="mt-10 grid grid-cols-1 md:grid-cols-3 gap-6">
          {pricingPlans.map((plan) => (
            <div
              key={plan.name}
              className={`rounded-3xl border border-border/70 bg-card/80 p-6 ${
                plan.popular ? "accent-ring" : ""
              }`}
            >
              <div className="flex items-center justify-between">
                <div className="text-sm font-semibold text-foreground">{plan.name}</div>
                {plan.popular && (
                  <span className="rounded-full border border-primary/30 bg-primary/10 px-3 py-1 text-xs font-semibold text-primary">
                    Popular
                  </span>
                )}
              </div>
              <div className="mt-4 flex items-baseline gap-2">
                <div className="text-3xl font-semibold text-foreground">
                  {isAnnual ? plan.annualPrice : plan.monthlyPrice}
                </div>
                <span className="text-sm text-muted-foreground">/month</span>
              </div>
              <p className="mt-2 text-sm text-muted-foreground">{plan.description}</p>
              <div className="mt-6">
                <Button
                  variant={plan.popular ? "default" : "outline"}
                  className="w-full rounded-full"
                >
                  {plan.buttonText}
                </Button>
              </div>
              <div className="mt-6 space-y-3 text-sm text-muted-foreground">
                {plan.features.map((feature) => (
                  <div key={feature} className="flex items-start gap-2">
                    <Check className="h-4 w-4 text-primary" />
                    <span>{feature}</span>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}

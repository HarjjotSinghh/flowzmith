"use client"

import type React from "react"
import { useState } from "react"
import { ChevronDown } from "lucide-react"

const faqData = [
  {
    question: "What is Flowzmith and who is it for?",
    answer:
      "Flowzmith is an AI-powered development platform designed for Flow builders, teams, and organizations. It accelerates contract creation, testing, and deployment from a single workspace.",
  },
  {
    question: "How does Flowzmith's AI code review work?",
    answer:
      "Our AI analyzes your code in real-time, providing suggestions, highlighting risks, and aligning outputs with your team's standards and best practices.",
  },
  {
    question: "Can I integrate Flowzmith with my existing tools?",
    answer:
      "Yes. Flowzmith connects to your existing stack through MCP integrations, enabling secure access to Git, documentation, and CI workflows.",
  },
  {
    question: "What's included in the free plan?",
    answer:
      "The free plan includes core AI suggestions, a single MCP server, up to two coding agents, and test deployments to help you get started.",
  },
  {
    question: "How do parallel coding agents work?",
    answer:
      "Parallel agents can draft code, review, and optimize simultaneously, reducing turnaround time on larger contract updates.",
  },
  {
    question: "Is my code secure with Flowzmith?",
    answer:
      "We use encrypted storage, secure access controls, and optional on-prem deployments. Your code remains private and never leaves your environment without permission.",
  },
]

interface FAQItemProps {
  question: string
  answer: string
  isOpen: boolean
  onToggle: () => void
}

const FAQItem = ({ question, answer, isOpen, onToggle }: FAQItemProps) => {
  const handleClick = (e: React.MouseEvent) => {
    e.preventDefault()
    onToggle()
  }

  return (
    <div
      className="w-full overflow-hidden rounded-2xl border border-border/70 bg-card/80 transition-all duration-300"
      onClick={handleClick}
    >
      <div className="flex w-full items-center justify-between gap-5 px-6 py-4 text-left">
        <div className="flex-1 text-base font-medium text-foreground">{question}</div>
        <ChevronDown
          className={`h-5 w-5 text-muted-foreground transition-transform ${
            isOpen ? "rotate-180" : "rotate-0"
          }`}
        />
      </div>
      <div
        className={`overflow-hidden transition-all duration-300 ${
          isOpen ? "max-h-80 opacity-100" : "max-h-0 opacity-0"
        }`}
      >
        <div className="px-6 pb-5 text-sm text-muted-foreground">{answer}</div>
      </div>
    </div>
  )
}

export function FAQSection() {
  const [openItems, setOpenItems] = useState<Set<number>>(new Set())
  const toggleItem = (index: number) => {
    const newOpenItems = new Set(openItems)
    if (newOpenItems.has(index)) {
      newOpenItems.delete(index)
    } else {
      newOpenItems.add(index)
    }
    setOpenItems(newOpenItems)
  }

  return (
    <section className="py-16">
      <div className="mx-auto w-full max-w-6xl px-6">
        <div className="text-center">
          <h2 className="text-3xl md:text-4xl font-display font-semibold text-foreground">
            Frequently asked questions
          </h2>
          <p className="mt-4 text-lg text-muted-foreground max-w-2xl mx-auto">
            Everything you need to know about Flowzmith and how it supports your Flow development workflow.
          </p>
        </div>
        <div className="mt-10 mx-auto max-w-3xl space-y-4">
          {faqData.map((faq, index) => (
            <FAQItem key={index} {...faq} isOpen={openItems.has(index)} onToggle={() => toggleItem(index)} />
          ))}
        </div>
      </div>
    </section>
  )
}

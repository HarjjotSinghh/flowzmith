"use client"

import type React from "react"
import { useState } from "react"
import { ChevronDown, Plus, Minus } from "lucide-react"
import { motion, AnimatePresence } from "framer-motion"
import { Button } from "@/components/ui/button"

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
  index: number
}

const FAQItem = ({ question, answer, isOpen, onToggle, index }: FAQItemProps) => {
  return (
    <motion.div
      initial={{ opacity: 0, x: -20 }}
      whileInView={{ opacity: 1, x: 0 }}
      viewport={{ once: true }}
      transition={{ delay: index * 0.1 }}
      className={`w-full overflow-hidden border-2 border-foreground bg-background transition-all duration-300 ${isOpen ? "shadow-[4px_4px_0px_0px_rgba(204,255,0,1)]" : "hover:bg-muted/5"
        }`}
    >
      <button
        onClick={onToggle}
        className="flex w-full items-center justify-between gap-5 px-6 py-5 text-left group"
      >
        <div className="flex items-center gap-4">
          <span className="text-xs font-black text-accent bg-black px-2 py-0.5">
            {index < 9 ? `0${index + 1}` : index + 1}
          </span>
          <div className="flex-1 text-base font-black text-foreground uppercase tracking-tight group-hover:text-accent transition-colors">
            {question}
          </div>
        </div>
        <div className={`transition-all duration-300 ${isOpen ? "rotate-180 text-accent" : "text-foreground"}`}>
          {isOpen ? <Minus className="h-5 w-5" /> : <Plus className="h-5 w-5" />}
        </div>
      </button>

      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: "auto", opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.3, ease: "easeInOut" }}
          >
            <div className="px-16 pb-6 text-sm font-bold text-foreground/80 uppercase leading-relaxed border-t-2 border-foreground/5 pt-4 italic">
              <span className="text-accent mr-2 font-black">{">"}</span>
              {answer}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  )
}

export function FAQSection() {
  const [openIndex, setOpenIndex] = useState<number | null>(0)

  const toggleItem = (index: number) => {
    setOpenIndex(openIndex === index ? null : index)
  }

  return (
    <section className="py-24 bg-background border-t-2 border-foreground border-x-2 border-foreground mx-auto max-w-[1400px] lg:px-16">
      <div className="mx-auto w-full max-w-4xl">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="flex flex-col items-center text-center gap-6 mb-16"
        >
          <div className="bg-accent text-black font-black px-4 py-1 text-xs tracking-[0.3em]">
            KNOWLEDGE BASE
          </div>
          <h2 className="text-4xl md:text-6xl font-black text-foreground tracking-tighter uppercase leading-none">
            FREQUENTLY ASKED QUESTIONS.
          </h2>
          <p className="text-lg md:text-xl font-bold text-foreground/80 max-w-2xl">
            EVERYTHING YOU NEED TO KNOW ABOUT FLOWZMITH AND HOW IT SUPPORTS YOUR FLOW DEVELOPMENT WORKFLOW.
          </p>
        </motion.div>

        <div className="space-y-4">
          {faqData.map((faq, index) => (
            <FAQItem
              key={index}
              {...faq}
              index={index}
              isOpen={openIndex === index}
              onToggle={() => toggleItem(index)}
            />
          ))}
        </div>

        <motion.div
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          viewport={{ once: true }}
          transition={{ delay: 0.5 }}
          className="mt-16 p-8 border-4 border-dashed border-foreground/20 text-center"
        >
          <p className="text-xs font-black text-foreground/80 uppercase tracking-widest mb-4">STILL HAVE QUESTIONS?</p>
          <Button variant="terminal" size="lg">OPEN SUPPORT TICKET</Button>
        </motion.div>
      </div>
    </section>
  )
}

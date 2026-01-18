"use client"

import { SubpageLayout } from "@/components/subpage-layout"
import { AnimatedSection } from "@/components/animated-section"
import { Copy, Terminal } from "lucide-react"

export default function APIPage() {
  const codeSnippet = `POST /v1/contracts/generate
{
  "prompt": "NFT Marketplace with royalties",
  "engine": "llm-core-v4",
  "security_level": "audit-ready"
}`

  return (
    <SubpageLayout 
      title="INTERFACE." 
      subtitle="INTEGRATE FLOWZMITH INTELLIGENCE DIRECTLY INTO YOUR STACK."
      category="Resources // endpoint"
    >
      <div className="space-y-16">
        <AnimatedSection delay={0.2}>
          <div className="grid grid-cols-1 lg:grid-cols-[1fr_500px] gap-12">
            <div className="space-y-8">
              <h2 className="text-4xl font-black uppercase tracking-tighter">API ACCESS</h2>
              <p className="text-xl font-bold uppercase text-foreground/80 leading-snug">
                WE PROVIDE A ROBUST REST INTERFACE FOR PROGRAMMATIC SMART CONTRACT GENERATION, VALIDATION, AND DEPLOYMENT.
              </p>
              <div className="flex gap-4">
                <button className="h-12 px-6 bg-accent text-black font-black uppercase border-2 border-foreground hover:bg-black hover:text-accent transition-all text-xs">
                  GENERATE API KEY
                </button>
                <button className="h-12 px-6 border-2 border-foreground font-black uppercase hover:bg-foreground hover:text-background transition-all text-xs">
                  API DOCS →
                </button>
              </div>
            </div>

            <div className="border-4 border-foreground bg-black overflow-hidden relative group">
              <div className="p-4 bg-muted/20 border-b-2 border-foreground flex justify-between items-center">
                <div className="flex gap-2">
                  <div className="w-3 h-3 bg-red-500 rounded-full" />
                  <div className="w-3 h-3 bg-yellow-500 rounded-full" />
                  <div className="w-3 h-3 bg-green-500 rounded-full" />
                </div>
                <button className="text-[10px] font-black text-accent/50 group-hover:text-accent transition-colors flex items-center gap-2">
                  COPY SNIPPET <Copy className="h-3 w-3" />
                </button>
              </div>
              <div className="p-6 font-mono text-sm overflow-x-auto">
                <pre className="text-accent">
                  {codeSnippet}
                </pre>
              </div>
            </div>
          </div>
        </AnimatedSection>

        <AnimatedSection delay={0.3}>
          <div className="border-2 border-foreground">
            <div className="bg-foreground text-background p-4 flex items-center gap-3">
              <Terminal className="h-5 w-5" />
              <h3 className="text-sm font-black uppercase tracking-widest">SYSTEM ENDPOINTS</h3>
            </div>
            <div className="divide-y-2 divide-foreground/10">
              {[
                { method: "POST", path: "/generate", desc: "CREATE NEW CADENCE CONTRACT FROM PROMPT" },
                { method: "GET", path: "/validate", desc: "RUN SECURITY CHECKS ON EXISTING CODE" },
                { method: "POST", path: "/deploy", desc: "EXECUTE ON-CHAIN DEPLOYMENT" },
                { method: "GET", path: "/usage", desc: "RETRIEVE RESOURCE ALLOCATION DATA" },
              ].map((endpoint) => (
                <div key={endpoint.path} className="p-6 flex flex-col md:flex-row md:items-center gap-6 group hover:bg-accent/5 transition-colors">
                  <div className="w-24 px-3 py-1 bg-black text-accent font-black text-center text-xs">
                    {endpoint.method}
                  </div>
                  <div className="font-mono text-lg font-black">{endpoint.path}</div>
                  <div className="md:ml-auto text-xs font-bold uppercase text-foreground/50">{endpoint.desc}</div>
                </div>
              ))}
            </div>
          </div>
        </AnimatedSection>
      </div>
    </SubpageLayout>
  )
}

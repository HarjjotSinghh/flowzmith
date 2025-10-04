import { Button } from "@/components/ui/button"
import Link from "next/link"
import { Trophy, ArrowRight } from "lucide-react"

export function CTASection() {
  return (
    <section className="w-full py-20 md:py-32 px-5 relative overflow-hidden">
      {/* Background Effects */}
      <div className="absolute inset-0" />
      <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-primary/20 rounded-full filter blur-3xl" />
      <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-accent/20 rounded-full filter blur-3xl" />

      <div className="relative z-10 max-w-6xl mx-auto">
        {/* Hackathon Achievement Banner */}
        <div className="text-center mb-16">
          <div className="inline-flex items-center gap-3 px-6 py-3 bg-gradient-to-r from-primary/20 to-primary-dark/20 border border-primary/30 rounded-full text-sm font-medium text-primary backdrop-blur-sm mb-8">
            <Trophy className="w-5 h-5" />
            Modern Stack Hackathon 2025 - Official Submission
            <Trophy className="w-5 h-5" />
          </div>
{/* 
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-12">
            <div className="text-center">
              <div className="w-20 h-20 bg-purple-500/20 rounded-2xl flex items-center justify-center mx-auto mb-4">
                <Zap className="w-10 h-10 text-purple-400" />
              </div>
              <h3 className="text-xl font-bold text-white mb-2">$25K Prize Pool</h3>
              <p className="text-white/60">Competing for the top innovation award</p>
            </div>

            <div className="text-center">
              <div className="w-20 h-20 bg-green-500/20 rounded-2xl flex items-center justify-center mx-auto mb-4">
                <Star className="w-10 h-10 text-green-400" />
              </div>
              <h3 className="text-xl font-bold text-white mb-2">Complete Integration</h3>
              <p className="text-white/60">Convex + OpenAI + Firecrawl fully implemented</p>
            </div>

            <div className="text-center">
              <div className="w-20 h-20 bg-blue-500/20 rounded-2xl flex items-center justify-center mx-auto mb-4">
                <ArrowRight className="w-10 h-10 text-blue-400" />
              </div>
              <h3 className="text-xl font-bold text-white mb-2">Production Ready</h3>
              <p className="text-white/60">Live demo, real-time features, scalable architecture</p>
            </div>
          </div> */}

          {/* Main CTA */}
          <div className="bg-card/50 border border-border rounded-3xl p-12 backdrop-blur-sm">
            <h2 className="text-4xl md:text-6xl font-bold text-foreground mb-6 leading-tight">
              The Future of Web3
              <br />
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-primary to-primary-dark">
                Development Starts Here
              </span>
            </h2>

            <p className="text-xl text-muted-foreground max-w-3xl mx-auto mb-8 leading-relaxed">
              Experience the revolutionary platform that showcases the perfect integration of modern stack technologies.
              Built to demonstrate innovation, real-time collaboration, and intelligent automation.
            </p>

            <div className="flex flex-col sm:flex-row gap-4 justify-center mb-8">
              <Link href="/login">
                <Button className="bg-gradient-to-r from-primary to-primary-dark hover:from-primary-dark hover:to-primary text-primary-foreground px-8 py-4 rounded-full font-semibold text-lg shadow-xl transition-all duration-300 ">
                  Start Building Now
                  <ArrowRight className="w-5 h-5 ml-2" />
                </Button>
              </Link>

              <Link href="https://www.youtube.com/watch?v=LL6dfPs0COo" target="_blank">
                <Button variant="outline" className="border-primary/50 text-primary hover:bg-primary/10 px-8 py-4 rounded-full font-semibold text-lg transition-all duration-300">
                  <Trophy className="w-5 h-5 mr-2" />
                  Judge Demo
                </Button>
              </Link>
            </div>

            {/* Quick Tech Summary */}
            <div className="flex justify-center items-center gap-6 text-muted-foreground text-sm">
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 bg-primary rounded-full" />
                <span>Convex Real-time</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 bg-accent-foreground rounded-full" />
                <span>OpenAI GPT-5</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 bg-secondary rounded-full" />
                <span>Firecrawl Data</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 bg-primary rounded-full" />
                <span>Flow Blockchain</span>
              </div>
            </div>
          </div>

          {/* Final Appeal to Judges */}
          <div className="mt-12 p-6 bg-gradient-to-r from-primary/10 to-primary-dark/10 border border-primary/30 rounded-2xl">
            <h3 className="text-xl font-semibold text-foreground mb-3">
              For the Modern Stack Hackathon Judges
            </h3>
            <p className="text-muted-foreground leading-relaxed max-w-4xl mx-auto">
              Flowzmith represents the pinnacle of modern web development, combining real-time database functionality (Convex),
              advanced AI intelligence (OpenAI), and comprehensive data crawling (Firecrawl) to create a platform that truly
              showcases the power of today's technology stack. Every feature is production-ready, every integration is seamless,
              and every user experience is designed to impress.
            </p>
          </div>
        </div>
      </div>
    </section>
  )
}
import { Sparkles, Database, Bot, Globe } from "lucide-react"
import { motion } from "framer-motion"
import { MagicCard } from "@/components/ui/magic-card"
import { AnimatedShinyText } from "@/components/ui/animated-shiny-text"
import Aurora from "./Aurora"

const TechCard = ({
  icon: Icon,
  title,
  description,
  features,
  gradient,
  index
}: {
  icon: React.ComponentType<any>,
  title: string,
  description: string,
  features: string[],
  gradient: string,
  index: number
}) => (
  <motion.div
    initial={{ opacity: 0, y: 50 }}
    whileInView={{ opacity: 1, y: 0 }}
    viewport={{ once: true, amount: 0.3 }}
    transition={{ duration: 0.6, delay: index * 0.1 }}
    whileHover={{ y: -10 }}
  >
    <MagicCard
      className={`overflow-hidden rounded-2xl border border-border flex flex-col relative bg-gradient-to-br ${gradient} hover-lift group cursor-pointer`}
      gradientSize={300}
      gradientOpacity={0.3}
    >
      <div className="absolute inset-0 bg-muted/10 backdrop-blur-sm" />

      <div className="p-6 flex flex-col gap-4 relative z-10">
        <motion.div
          className="flex items-center gap-3"
          whileHover={{ scale: 1.05 }}
          transition={{ type: "spring", stiffness: 400 }}
        >
          <motion.div
            className="p-2 bg-card rounded-lg"
            whileHover={{ rotate: 360 }}
            transition={{ duration: 0.6 }}
          >
            <Icon className="w-6 h-6 text-foreground" />
          </motion.div>
          <h3 className="text-xl font-semibold text-foreground">
            <AnimatedShinyText className="inline-block">
              {title}
            </AnimatedShinyText>
          </h3>
        </motion.div>

        <p className="text-muted-foreground text-sm leading-relaxed">{description}</p>

        <div className="space-y-2">
          {features.map((feature, featureIndex) => (
            <motion.div
              key={featureIndex}
              className="flex items-center gap-2"
              initial={{ opacity: 0, x: -20 }}
              whileInView={{ opacity: 1, x: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.4, delay: index * 0.1 + featureIndex * 0.05 }}
            >
              <motion.div
                className="w-1.5 h-1.5 bg-primary rounded-full"
                whileHover={{ scale: 1.5 }}
              />
              <span className="text-muted-foreground text-xs group-hover:text-foreground transition-colors">
                {feature}
              </span>
            </motion.div>
          ))}
        </div>
      </div>

      <div className="mt-auto p-6 pt-0">
        <div className="h-2 bg-card rounded-full overflow-hidden">
          <motion.div
            className="h-full bg-gradient-to-r from-primary to-primary-dark rounded-full"
            initial={{ width: 0 }}
            whileInView={{ width: '75%' }}
            viewport={{ once: true }}
            transition={{ duration: 1, delay: index * 0.1 + 0.5 }}
          />
        </div>
      </div>
    </MagicCard>
  </motion.div>
)

export function BentoSection() {
  return (
    <section className="w-full px-5 py-16 relative overflow-hidden">
      {/* Enhanced Background with Aurora */}
      <div className="absolute inset-0 z-0">
        <Aurora
          colorStops={["#78fcd6", "#5effba", "#78fcd6"]}
          blend={0.1}
        />
        <div className="absolute inset-0" />
        <motion.div
          className="absolute top-1/4 left-1/4 w-96 h-96 bg-primary/10 rounded-full filter blur-3xl"
          animate={{
            x: [0, 50, 0],
            y: [0, -30, 0],
          }}
          transition={{
            duration: 10,
            repeat: Infinity,
            ease: "easeInOut"
          }}
        />
        <motion.div
          className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-primary/10 rounded-full filter blur-3xl"
          animate={{
            x: [0, -50, 0],
            y: [0, 30, 0],
          }}
          transition={{
            duration: 12,
            repeat: Infinity,
            ease: "easeInOut"
          }}
        />
      </div>

      <div className="relative z-10 max-w-7xl mx-auto">
        {/* Animated Header */}
        <motion.div
          className="text-center mb-16"
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.8 }}
        >
          <motion.div
            className="inline-flex items-center gap-2 px-4 py-2 bg-card/50 border border-border rounded-full text-sm font-medium text-foreground backdrop-blur-sm mb-6 hover-lift"
            whileHover={{ scale: 1.05 }}
            transition={{ type: "spring", stiffness: 400 }}
          >
            <motion.div
              animate={{ rotate: 360 }}
              transition={{ duration: 3, repeat: Infinity, ease: "linear" }}
            >
              <Sparkles className="w-4 h-4" />
            </motion.div>
            <AnimatedShinyText>Modern Stack Integration</AnimatedShinyText>
          </motion.div>

          <motion.h2
            className="text-4xl md:text-6xl font-bold text-foreground mb-6 leading-tight"
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6, delay: 0.2 }}
          >
            Three Technologies.
            <br />
            <motion.span
              className="text-transparent bg-clip-text bg-gradient-to-r from-primary to-primary-dark inline-block"
              whileHover={{ scale: 1.05 }}
              transition={{ type: "spring", stiffness: 400 }}
            >
              Infinite Possibilities
            </motion.span>
          </motion.h2>

          <motion.p
            className="text-xl text-muted-foreground max-w-3xl mx-auto leading-relaxed"
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6, delay: 0.4 }}
          >
            Experience the power of real-time collaboration, AI intelligence, and web crawling combined in one revolutionary platform
          </motion.p>
        </motion.div>

        {/* Tech Cards Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {/* Convex Card */}
          <TechCard
            icon={Database}
            title="Real-time with Convex"
            description="Experience the future of collaborative smart contract development with live synchronization across all devices."
            features={[
              "Real-time collaboration sessions",
              "Live deployment tracking",
              "Instant notifications",
              "Multi-user contract editing",
              "Automatic data synchronization"
            ]}
            gradient="from-primary/20 to-primary/40"
            index={0}
          />

          {/* OpenAI Card */}
          <TechCard
            icon={Bot}
            title="AI with OpenAI"
            description="Generate, optimize, and deploy production-ready Cadence smart contracts using advanced AI technology."
            features={[
              "Natural language to code",
              "Intelligent code optimization",
              "Security pattern detection",
              "Automated testing suggestions",
              "Context-aware generation"
            ]}
            gradient="from-accent/20 to-accent/40"
            index={1}
          />

          {/* Firecrawl Card */}
          <TechCard
            icon={Globe}
            title="Intelligence with Firecrawl"
            description="Access the most comprehensive and up-to-date Flow ecosystem documentation for smarter AI training."
            features={[
              "96% web coverage capability",
              "Real-time documentation updates",
              "Smart content extraction",
              "Sub-second performance",
              "Interactive scraping technology"
            ]}
            gradient="from-secondary/20 to-secondary/40"
            index={2}
          />
        </div>

        {/* Animated Integration Showcase */}
        <motion.div
          className="mt-16 text-center"
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.8, delay: 0.6 }}
        >
          <motion.div
            className="inline-flex items-center gap-8 px-8 py-6 bg-card/50 border border-border rounded-2xl backdrop-blur-sm hover-lift group"
            whileHover={{ scale: 1.02 }}
            transition={{ type: "spring", stiffness: 400 }}
          >
            <motion.div
              className="flex items-center gap-3"
              whileHover={{ scale: 1.1 }}
              transition={{ type: "spring", stiffness: 400 }}
            >
              <motion.div
                className="w-12 h-12 bg-primary/20 rounded-lg flex items-center justify-center"
                whileHover={{ rotate: 360 }}
                transition={{ duration: 0.6 }}
              >
                <Database className="w-6 h-6 text-primary" />
              </motion.div>
              <div className="text-left">
                <div className="text-sm font-medium text-foreground group-hover:text-primary transition-colors">Convex</div>
                <div className="text-xs text-muted-foreground">Real-time</div>
              </div>
            </motion.div>

            <motion.div
              className="text-muted-foreground text-2xl"
              animate={{ scale: [1, 1.2, 1] }}
              transition={{ duration: 2, repeat: Infinity, ease: "easeInOut" }}
            >
              +
            </motion.div>

            <motion.div
              className="flex items-center gap-3"
              whileHover={{ scale: 1.1 }}
              transition={{ type: "spring", stiffness: 400 }}
            >
              <motion.div
                className="w-12 h-12 bg-accent/20 rounded-lg flex items-center justify-center"
                whileHover={{ rotate: 360 }}
                transition={{ duration: 0.6 }}
              >
                <Bot className="w-6 h-6 text-accent-foreground" />
              </motion.div>
              <div className="text-left">
                <div className="text-sm font-medium text-foreground group-hover:text-accent-foreground transition-colors">OpenAI</div>
                <div className="text-xs text-muted-foreground">Intelligence</div>
              </div>
            </motion.div>

            <motion.div
              className="text-muted-foreground text-2xl"
              animate={{ scale: [1, 1.2, 1] }}
              transition={{ duration: 2, repeat: Infinity, ease: "easeInOut", delay: 0.5 }}
            >
              +
            </motion.div>

            <motion.div
              className="flex items-center gap-3"
              whileHover={{ scale: 1.1 }}
              transition={{ type: "spring", stiffness: 400 }}
            >
              <motion.div
                className="w-12 h-12 bg-secondary/20 rounded-lg flex items-center justify-center"
                whileHover={{ rotate: 360 }}
                transition={{ duration: 0.6 }}
              >
                <Globe className="w-6 h-6 text-secondary-foreground" />
              </motion.div>
              <div className="text-left">
                <div className="text-sm font-medium text-foreground group-hover:text-secondary-foreground transition-colors">Firecrawl</div>
                <div className="text-xs text-muted-foreground">Data</div>
              </div>
            </motion.div>

            <motion.div
              className="text-muted-foreground text-2xl"
              animate={{ scale: [1, 1.2, 1] }}
              transition={{ duration: 2, repeat: Infinity, ease: "easeInOut", delay: 1 }}
            >
              =
            </motion.div>

            <motion.div
              className="flex items-center gap-3"
              whileHover={{ scale: 1.15 }}
              transition={{ type: "spring", stiffness: 400 }}
            >
              <motion.div
                className="w-12 h-12 bg-gradient-to-r from-primary/20 to-primary-dark/20 rounded-lg flex items-center justify-center animate-pulse-glow"
                whileHover={{ rotate: 360 }}
                transition={{ duration: 0.6 }}
              >
                <motion.div
                  animate={{ rotate: 360 }}
                  transition={{ duration: 3, repeat: Infinity, ease: "linear" }}
                >
                  <Sparkles className="w-6 h-6 text-foreground" />
                </motion.div>
              </motion.div>
              <div className="text-left">
                <div className="text-sm font-medium text-foreground">
                  <AnimatedShinyText>Flowzmith</AnimatedShinyText>
                </div>
                <div className="text-xs text-muted-foreground">Magic</div>
              </div>
            </motion.div>
          </motion.div>
        </motion.div>
      </div>
    </section>
  )
}

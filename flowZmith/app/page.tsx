'use client'
import { HeroSection } from "@/components/hero-section"
import { DashboardPreview } from "@/components/dashboard-preview"
import { SocialProof } from "@/components/social-proof"
import { BentoSection } from "@/components/bento-section"
import LiveDemoSection from "@/components/live-demo-section"
import { LargeTestimonial } from "@/components/large-testimonial"
import { PricingSection } from "@/components/pricing-section"
import { TestimonialGridSection } from "@/components/testimonial-grid-section"
import { FAQSection } from "@/components/faq-section"
import { CTASection } from "@/components/cta-section"
import { FooterSection } from "@/components/footer-section"
import { AnimatedSection } from "@/components/animated-section"
import Aurora from "@/components/Aurora"
import { motion } from "framer-motion"

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-background relative overflow-hidden pb-0">
      {/* Global Aurora Background */}
      <div className="fixed inset-0 z-0 opacity-50">
        <Aurora
          colorStops={["#78fcd6", "#5effba", "#78fcd6"]}
          blend={0.4}
        />
      </div>

      <div className="relative z-10">
        <main className=" mx-auto relative">
          <HeroSection />
          {/* Dashboard Preview Wrapper */}
          <div className="absolute bottom-[-150px] md:bottom-[-400px] left-1/2 transform -translate-x-1/2 z-30">
            <AnimatedSection>
              <DashboardPreview />
            </AnimatedSection>
          </div>
        </main>
        <AnimatedSection className="relative z-10 mx-auto px-0 mt-[411px] md:mt-[400px]" delay={0.1} animation="fadeInUp">
          <SocialProof />
        </AnimatedSection>
        <AnimatedSection id="features-section" className="relative z-10 mx-auto mt-0" delay={0.2} animation="scaleIn">
          <BentoSection />
        </AnimatedSection>
        <AnimatedSection className="relative z-10 mx-auto mt-0" delay={0.3} animation="fadeInLeft">
          <LiveDemoSection />
        </AnimatedSection>
        <AnimatedSection className="relative z-10 mx-auto mt-8 md:mt-16" delay={0.2} animation="fadeInRight">
          <LargeTestimonial />
        </AnimatedSection>
        <AnimatedSection
          id="pricing-section"
          className="relative z-10 mx-auto mt-8 md:mt-16"
          delay={0.2}
          animation="blurIn"
        >
          <PricingSection />
        </AnimatedSection>
        <AnimatedSection
          id="testimonials-section"
          className="relative z-10 mx-auto mt-8 md:mt-16"
          delay={0.2}
          animation="fadeInUp"
        >
          <TestimonialGridSection />
        </AnimatedSection>
        <AnimatedSection id="faq-section" className="relative z-10 mx-auto mt-8 md:mt-16" delay={0.2} animation="fadeInDown">
          <FAQSection />
        </AnimatedSection>
        <AnimatedSection className="relative z-10 mx-auto mt-8 md:mt-16" delay={0.2} animation="scaleIn">
          <CTASection />
        </AnimatedSection>
        <AnimatedSection className="relative z-10 mx-auto mt-8 md:mt-16" delay={0.2} animation="fadeInUp">
        <div className="absolute inset-0 scale-y-[-1] -z-[10] opacity-30">
        <Aurora colorStops={["#78fcd6", "#5effba", "#78fcd6"]} blend={0.9} amplitude={0.3}  />
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
            ease: "easeInOut",
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
            ease: "easeInOut",
          }}
        />
      </div>
          <FooterSection />
        </AnimatedSection>
      </div>
    </div>
  )
}

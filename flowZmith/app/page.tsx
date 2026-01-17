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

export default function LandingPage() {
  return (
    <div className="min-h-screen">
      <main className="mx-auto">
        <HeroSection />

        <div className="mx-auto max-w-6xl px-6">
          <AnimatedSection className="mt-16" delay={0.1} animation="fadeInUp">
            <DashboardPreview />
          </AnimatedSection>
        </div>

        <AnimatedSection className="mt-20" delay={0.1} animation="fadeInUp">
          <SocialProof />
        </AnimatedSection>

        <AnimatedSection id="features-section" className="mt-20" delay={0.2} animation="fadeInUp">
          <BentoSection />
        </AnimatedSection>

        <AnimatedSection className="mt-20" delay={0.3} animation="fadeInUp">
          <LiveDemoSection />
        </AnimatedSection>

        <AnimatedSection className="mt-20" delay={0.2} animation="fadeInUp">
          <LargeTestimonial />
        </AnimatedSection>

        <AnimatedSection id="pricing-section" className="mt-20" delay={0.2} animation="fadeInUp">
          <PricingSection />
        </AnimatedSection>

        <AnimatedSection id="testimonials-section" className="mt-20" delay={0.2} animation="fadeInUp">
          <TestimonialGridSection />
        </AnimatedSection>

        <AnimatedSection id="faq-section" className="mt-20" delay={0.2} animation="fadeInUp">
          <FAQSection />
        </AnimatedSection>

        <AnimatedSection className="mt-20" delay={0.2} animation="fadeInUp">
          <CTASection />
        </AnimatedSection>

        <AnimatedSection className="mt-16" delay={0.2} animation="fadeInUp">
          <FooterSection />
        </AnimatedSection>
      </main>
    </div>
  )
}

'use client'

import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { AnimatedSection } from '@/components/animated-section'
import { useWallet, PLANS } from '@/contexts/WalletProviderHybrid'
import { Header } from '@/components/header'
import {
  CreditCard,
  Zap,
  Crown,
  Check,
  Loader2,
  AlertCircle,
  ExternalLink,
  Wallet,
  ArrowRight,
  Shield
} from 'lucide-react'
import { motion } from "framer-motion"

export default function PlansPage() {
  const { wallet, connect, switchToFlowEVM, sendPayment, isConnecting } = useWallet()
  const [selectedPlan, setSelectedPlan] = useState<string | null>(null)
  const [isProcessing, setIsProcessing] = useState(false)
  const [txHash, setTxHash] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)

  const handlePurchase = async (planId: string) => {
    const plan = PLANS.find(p => p.id === planId)
    if (!plan) return

    setSelectedPlan(planId)
    setIsProcessing(true)
    setError(null)

    try {
      if (!wallet.isConnected) {
        await connect()
        return
      }

      if (wallet.chainId !== 747) {
        await switchToFlowEVM()
        return
      }

      if (wallet.balance && parseFloat(wallet.balance) < plan.price) {
        setError('Insufficient FLOW balance')
        return
      }

      const result = await sendPayment(plan)

      if (result.success && result.txHash) {
        setTxHash(result.txHash)
      } else {
        setError(result.error || 'Payment failed')
      }
    } catch (err) {
      setError('An unexpected error occurred')
      console.error(err)
    } finally {
      setIsProcessing(false)
    }
  }

  const getPlanIcon = (planId: string) => {
    switch (planId) {
      case 'starter':
        return <CreditCard className="w-6 h-6" />
      case 'pro':
        return <Zap className="w-6 h-6" />
      case 'enterprise':
        return <Crown className="w-6 h-6" />
      default:
        return <CreditCard className="w-6 h-6" />
    }
  }

  return (
    <div className="min-h-screen bg-background font-mono text-foreground border-x-2 border-foreground mx-auto max-w-[1440px]">
      <Header />

      <main className="px-6 py-12">
        {/* Hero Section */}
        <AnimatedSection delay={0.1}>
          <div className="mb-16 border-b-2 border-foreground pb-12 flex flex-col md:flex-row md:items-end justify-between gap-8">
            <div className="max-w-3xl">
              <div className="inline-block bg-accent text-black font-black px-4 py-1 text-xs mb-6 tracking-widest">
                PROTOCOL ACCESS // PRICING MODULE
              </div>
              <h1 className="text-5xl md:text-7xl lg:text-8xl font-black tracking-tighter uppercase leading-[0.8]">
                CHOOSE YOUR<br />LEVEL.
              </h1>
              <p className="text-xl font-bold text-foreground/80 mt-8 border-l-4 border-accent pl-8 max-w-xl">
                SELECT THE OPTIMAL RESOURCE ALLOCATION FOR YOUR SMART CONTRACT ARCHITECTURE NEEDS.
              </p>
            </div>
            
            <div className="flex flex-col items-end gap-4">
              <div className="border-2 border-foreground p-4 bg-muted/5 w-full md:w-80">
                <div className="flex items-center justify-between mb-4">
                  <div className="text-[10px] font-black uppercase tracking-widest">WALLET STATUS</div>
                  <div className={`h-2 w-2 ${wallet.isConnected ? 'bg-accent animate-pulse' : 'bg-red-500'}`} />
                </div>
                
                {wallet.isConnected ? (
                  <div className="space-y-2">
                    <div className="flex justify-between items-center">
                      <span className="text-xs font-bold opacity-50 uppercase">BALANCE:</span>
                      <span className="text-lg font-black">{wallet.balance || '0'} FLOW</span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-xs font-bold opacity-50 uppercase">NETWORK:</span>
                      <span className="text-xs font-black bg-black text-accent px-1">
                        {wallet.chainId === 747 ? 'FLOW EVM' : 'WRONG NET'}
                      </span>
                    </div>
                  </div>
                ) : (
                  <Button 
                    onClick={connect} 
                    disabled={isConnecting}
                    className="w-full bg-accent text-black hover:bg-white transition-colors font-black uppercase text-xs h-10 border-2 border-foreground"
                  >
                    {isConnecting ? <Loader2 className="h-4 w-4 animate-spin mr-2" /> : <Wallet className="h-4 w-4 mr-2" />}
                    INITIALIZE WALLET
                  </Button>
                )}
              </div>
            </div>
          </div>
        </AnimatedSection>

        {/* Notifications */}
        <div className="space-y-4 mb-12">
          {txHash && (
            <AnimatedSection animation="fadeInUp">
              <div className="bg-accent/10 border-2 border-accent p-6 flex items-start gap-4 relative overflow-hidden group">
                <div className="absolute top-0 right-0 w-4 h-4 bg-accent" />
                <Check className="w-8 h-8 text-accent shrink-0" />
                <div>
                  <h3 className="text-xl font-black uppercase tracking-tight text-accent">TRANSACTION VERIFIED</h3>
                  <p className="font-bold text-sm mt-1">CREDITS HAVE BEEN ALLOCATED TO YOUR AGENT ID.</p>
                  <a
                    href={`https://evm.flowscan.io/tx/${txHash}`}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center gap-2 text-xs font-black bg-black text-white px-3 py-1 mt-4 hover:bg-accent hover:text-black transition-colors"
                  >
                    SCAN BLOCKCHAIN <ExternalLink className="w-3 h-3" />
                  </a>
                </div>
              </div>
            </AnimatedSection>
          )}

          {error && (
            <AnimatedSection animation="fadeInUp">
              <div className="bg-red-500/10 border-2 border-red-500 p-6 flex items-start gap-4 relative overflow-hidden">
                <div className="absolute top-0 right-0 w-4 h-4 bg-red-500" />
                <AlertCircle className="w-8 h-8 text-red-500 shrink-0" />
                <div>
                  <h3 className="text-xl font-black uppercase tracking-tight text-red-500">PAYMENT FAILED</h3>
                  <p className="font-bold text-sm mt-1">{error.toUpperCase()}</p>
                </div>
              </div>
            </AnimatedSection>
          )}
        </div>

        {/* Plans Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 border-2 border-foreground bg-foreground gap-[1px] mb-24">
          {PLANS.map((plan, index) => (
            <AnimatedSection key={plan.id} delay={index * 0.1} className="h-full">
              <div className={`group p-8 transition-all duration-300 ${plan.popular ? 'bg-accent/5 hover:bg-accent' : 'bg-background hover:bg-muted/10'} flex flex-col h-full cursor-default relative overflow-hidden border-none`}>
                {plan.popular && (
                  <div className="absolute top-0 right-0 bg-accent text-black font-black px-4 py-1 text-[10px] tracking-widest uppercase">
                    RECOMMENDED
                  </div>
                )}

                <div className={`flex h-16 w-16 items-center justify-center border-2 border-foreground bg-background group-hover:bg-black group-hover:border-black transition-colors duration-300`}>
                  <div className="group-hover:text-accent transition-colors duration-300">
                    {getPlanIcon(plan.id)}
                  </div>
                </div>

                <div className="mt-8 space-y-2">
                  <h3 className="text-3xl font-black tracking-tighter text-foreground group-hover:text-black transition-colors duration-300 uppercase leading-none">
                    {`[ ${plan.name} ]`}
                  </h3>
                  <p className="text-xs font-bold text-foreground/60 group-hover:text-black/60 uppercase tracking-widest">
                    {plan.description}
                  </p>
                </div>

                <div className="mt-8 pt-8 border-t-2 border-foreground/10 group-hover:border-black/10">
                  <div className="flex items-baseline gap-2 group-hover:text-black transition-colors">
                    <span className="text-5xl font-black tracking-tighter">{plan.price}</span>
                    <span className="text-xl font-black opacity-50">FLOW</span>
                  </div>
                  <div className="text-xs font-black mt-1 bg-black text-accent inline-block px-2 group-hover:bg-white group-hover:text-black transition-colors">
                    {plan.credits} CREDITS INCLUDED
                  </div>
                </div>

                <ul className="mt-8 space-y-3 flex-1">
                  {plan.features.map((feature, idx) => (
                    <li key={idx} className="flex items-start gap-3 text-sm font-bold group-hover:text-black transition-colors uppercase leading-tight">
                      <Check className="w-4 h-4 mt-0.5 shrink-0" />
                      <span>{feature}</span>
                    </li>
                  ))}
                </ul>

                <div className="mt-12">
                  <Button
                    onClick={() => handlePurchase(plan.id)}
                    disabled={isProcessing && selectedPlan === plan.id}
                    className={`w-full h-16 text-xl font-black uppercase transition-all border-2 border-foreground relative overflow-hidden group/btn ${
                      plan.popular 
                        ? 'bg-black text-white hover:text-black' 
                        : 'bg-background text-foreground hover:text-black'
                    }`}
                  >
                    <span className="relative z-10 flex items-center justify-center gap-2">
                      {isProcessing && selectedPlan === plan.id ? (
                        <>
                          <Loader2 className="w-6 h-6 animate-spin" />
                          PROCESSING
                        </>
                      ) : (
                        <>
                          {wallet.isConnected ? 'INITIALIZE PURCHASE' : 'CONNECT WALLET'}
                          <ArrowRight className="w-6 h-6 group-hover/btn:translate-x-2 transition-transform" />
                        </>
                      )}
                    </span>
                    <div className="absolute inset-0 bg-accent translate-y-full group-hover/btn:translate-y-0 transition-transform duration-300" />
                  </Button>
                </div>

                <div className="absolute bottom-0 right-0 w-0 h-0 border-b-[20px] border-l-[20px] border-b-transparent border-l-transparent group-hover:border-b-black transition-all duration-300" />
              </div>
            </AnimatedSection>
          ))}
        </div>

        {/* Info Section */}
        <AnimatedSection delay={0.5}>
          <div className="border-2 border-foreground p-12 bg-black text-white relative overflow-hidden">
            <div className="absolute top-0 right-0 p-4 opacity-10">
              <Shield className="w-32 h-32" />
            </div>
            
            <div className="relative z-10 max-w-4xl mx-auto text-center">
              <h2 className="text-4xl font-black tracking-tighter uppercase mb-12">
                SYSTEM DEPLOYMENT PROTOCOL
              </h2>
              <div className="grid md:grid-cols-3 gap-12 text-left">
                <div className="space-y-4">
                  <div className="w-12 h-12 border-2 border-accent flex items-center justify-center">
                    <Wallet className="w-6 h-6 text-accent" />
                  </div>
                  <h3 className="text-xl font-black uppercase tracking-tight">01. WALLET SYNC</h3>
                  <p className="text-sm font-bold text-white/60 uppercase leading-snug">
                    CONNECT YOUR EVM-COMPATIBLE WALLET TO THE FLOW MAINNET INFRASTRUCTURE.
                  </p>
                </div>
                <div className="space-y-4">
                  <div className="w-12 h-12 border-2 border-accent flex items-center justify-center">
                    <CreditCard className="w-6 h-6 text-accent" />
                  </div>
                  <h3 className="text-xl font-black uppercase tracking-tight">02. NODE SELECTION</h3>
                  <p className="text-sm font-bold text-white/60 uppercase leading-snug">
                    SELECT THE RESOURCE TIER THAT MATCHES YOUR ARCHITECTURAL COMPLEXITY.
                  </p>
                </div>
                <div className="space-y-4">
                  <div className="w-12 h-12 border-2 border-accent flex items-center justify-center">
                    <Zap className="w-6 h-6 text-accent" />
                  </div>
                  <h3 className="text-xl font-black uppercase tracking-tight">03. EXECUTE BUILD</h3>
                  <p className="text-sm font-bold text-white/60 uppercase leading-snug">
                    INSTANTLY ACTIVATE YOUR AI AGENTS AND START GENERATING CADENCE CODE.
                  </p>
                </div>
              </div>
            </div>
          </div>
        </AnimatedSection>
      </main>

      <footer className="border-t-2 border-foreground p-6 flex flex-col md:flex-row justify-between items-center gap-4 text-[10px] font-black uppercase opacity-50">
        <div className="flex gap-8">
          <span>ENCRYPTED_GATEWAY: RSA-4096</span>
          <span>LOCATION: FLOW_MAINNET_EVM</span>
        </div>
        <span>FLOWZMITH BILLING V1.2.0 // ALL RIGHTS RESERVED</span>
      </footer>
    </div>
  )
}
'use client'

import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { AnimatedSection } from '@/components/animated-section'
import { useWallet, PLANS } from '@/contexts/WalletProviderHybrid'
import {
  CreditCard,
  Zap,
  Crown,
  Check,
  Loader2,
  AlertCircle,
  ExternalLink,
  Wallet
} from 'lucide-react'

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
      // Check if wallet is connected
      if (!wallet.isConnected) {
        await connect()
        return
      }

      // Check if on correct network
      if (wallet.chainId !== 747) {
        await switchToFlowEVM()
        return
      }

      // Check balance
      if (wallet.balance && parseFloat(wallet.balance) < plan.price) {
        setError('Insufficient FLOW balance')
        return
      }

      // Send payment
      const result = await sendPayment(plan)

      if (result.success && result.txHash) {
        setTxHash(result.txHash)
        // Here you would typically update the user's credits in your backend
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
        return <CreditCard className="w-8 h-8" />
      case 'pro':
        return <Zap className="w-8 h-8" />
      case 'enterprise':
        return <Crown className="w-8 h-8" />
      default:
        return <CreditCard className="w-8 h-8" />
    }
  }

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <div className="border-b border-border">
        <div className="container mx-auto px-4 py-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-foreground">Choose Your Plan</h1>
              <p className="text-muted-foreground mt-2">
                Select the perfect plan for your smart contract development needs
              </p>
            </div>

            {/* Wallet Connection */}
            <div className="flex items-center gap-4">
              {wallet.isConnected ? (
                <div className="flex items-center gap-3">
                  <div className="text-sm">
                    <div className="text-muted-foreground">Balance</div>
                    <div className="font-semibold">{wallet.balance || '0'} FLOW</div>
                  </div>
                  <div className="text-sm text-right">
                    <div className="text-muted-foreground">Network</div>
                    <div className="font-semibold">
                      {wallet.chainId === 747 ? 'Flow EVM' : 'Wrong Network'}
                    </div>
                  </div>
                  <div className="text-sm text-right max-w-[120px]">
                    <div className="text-muted-foreground">Address</div>
                    <div className="font-semibold text-xs">
                      {wallet.address?.slice(0, 6)}...{wallet.address?.slice(-4)}
                    </div>
                  </div>
                </div>
              ) : (
                <Button onClick={connect} disabled={isConnecting}>
                  {isConnecting ? <Loader2 className="w-4 h-4 animate-spin mr-2" /> : <Wallet className="w-4 h-4 mr-2" />}
                  Connect Wallet
                </Button>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Success Message */}
      {txHash && (
        <div className="container mx-auto px-4 py-6">
          <Card className="border-green-500 bg-green-50">
            <CardContent className="p-6">
              <div className="flex items-center gap-3">
                <Check className="w-6 h-6 text-green-600" />
                <div>
                  <h3 className="font-semibold text-green-900">Payment Successful!</h3>
                  <p className="text-green-700 text-sm">
                    Your credits have been added to your account.
                  </p>
                  <a
                    href={`https://evm.flowscan.io/tx/${txHash}`}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center gap-1 text-green-600 hover:text-green-800 text-sm mt-2"
                  >
                    View transaction <ExternalLink className="w-3 h-3" />
                  </a>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Error Message */}
      {error && (
        <div className="container mx-auto px-4 py-6">
          <Card className="border-red-500 bg-red-50">
            <CardContent className="p-6">
              <div className="flex items-center gap-3">
                <AlertCircle className="w-6 h-6 text-red-600" />
                <div>
                  <h3 className="font-semibold text-red-900">Payment Failed</h3>
                  <p className="text-red-700 text-sm">{error}</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Plans Grid */}
      <div className="container mx-auto px-4 py-12">
        <div className="grid md:grid-cols-3 gap-8 max-w-6xl mx-auto">
          {PLANS.map((plan, index) => (
            <AnimatedSection key={plan.id} delay={index * 0.1}>
              <Card className={`relative h-full ${
                plan.popular
                  ? 'border-primary shadow-lg scale-105'
                  : 'border-border hover:border-primary/50'
              }`}>
                {plan.popular && (
                  <div className="absolute -top-3 left-1/2 transform -translate-x-1/2">
                    <div className="bg-primary text-primary-foreground px-4 py-1 rounded-full text-sm font-semibold">
                      Most Popular
                    </div>
                  </div>
                )}

                <CardHeader className="text-center pb-4">
                  <div className="flex justify-center mb-4">
                    <div className={`w-16 h-16 rounded-full flex items-center justify-center ${
                      plan.popular ? 'bg-primary/20' : 'bg-secondary/20'
                    }`}>
                      {getPlanIcon(plan.id)}
                    </div>
                  </div>
                  <CardTitle className={`text-2xl ${
                    plan.popular ? 'text-primary' : 'text-foreground'
                  }`}>
                    {plan.name}
                  </CardTitle>
                  <p className="text-muted-foreground">{plan.description}</p>
                  <div className="pt-4">
                    <div className="text-4xl font-bold text-foreground">
                      {plan.price} <span className="text-lg text-muted-foreground">FLOW</span>
                    </div>
                    <div className="text-sm text-muted-foreground">
                      {plan.credits} credits
                    </div>
                  </div>
                </CardHeader>

                <CardContent className="flex-1 flex flex-col">
                  <ul className="space-y-3 mb-8 flex-1">
                    {plan.features.map((feature, idx) => (
                      <li key={idx} className="flex items-center gap-3">
                        <Check className="w-5 h-5 text-green-600 flex-shrink-0" />
                        <span className="text-sm">{feature}</span>
                      </li>
                    ))}
                  </ul>

                  <Button
                    onClick={() => handlePurchase(plan.id)}
                    disabled={isProcessing && selectedPlan === plan.id}
                    className={`w-full ${
                      plan.popular
                        ? 'bg-primary hover:bg-primary/90'
                        : 'bg-primary hover:bg-primary/90'
                    }`}
                    size="lg"
                  >
                    {isProcessing && selectedPlan === plan.id ? (
                      <>
                        <Loader2 className="w-4 h-4 animate-spin mr-2" />
                        Processing...
                      </>
                    ) : (
                      <>
                        {wallet.isConnected ? 'Purchase Now' : 'Connect Wallet'}
                      </>
                    )}
                  </Button>
                </CardContent>
              </Card>
            </AnimatedSection>
          ))}
        </div>
      </div>

      {/* Info Section */}
      <div className="border-t border-border">
        <div className="container mx-auto px-4 py-12">
          <div className="max-w-4xl mx-auto text-center">
            <h2 className="text-2xl font-bold text-foreground mb-4">
              How It Works
            </h2>
            <div className="grid md:grid-cols-3 gap-8 mt-8">
              <div className="space-y-3">
                <div className="w-12 h-12 bg-primary/20 rounded-lg flex items-center justify-center mx-auto">
                  <Wallet className="w-6 h-6 text-primary" />
                </div>
                <h3 className="font-semibold">Connect Wallet</h3>
                <p className="text-sm text-muted-foreground">
                  Connect your EVM wallet and switch to Flow EVM network
                </p>
              </div>
              <div className="space-y-3">
                <div className="w-12 h-12 bg-primary/20 rounded-lg flex items-center justify-center mx-auto">
                  <CreditCard className="w-6 h-6 text-primary" />
                </div>
                <h3 className="font-semibold">Choose Plan</h3>
                <p className="text-sm text-muted-foreground">
                  Select the plan that best fits your development needs
                </p>
              </div>
              <div className="space-y-3">
                <div className="w-12 h-12 bg-primary/20 rounded-lg flex items-center justify-center mx-auto">
                  <Zap className="w-6 h-6 text-primary" />
                </div>
                <h3 className="font-semibold">Start Building</h3>
                <p className="text-sm text-muted-foreground">
                  Use your credits to generate smart contracts with AI
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
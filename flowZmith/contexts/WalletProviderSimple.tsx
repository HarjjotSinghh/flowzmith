'use client'

import { createContext, useContext, useState, ReactNode } from 'react'
import { WalletState, Plan } from '@/lib/web3/types'

interface WalletContextType {
  wallet: WalletState
  connect: () => void
  disconnect: () => void
  switchToFlowEVM: () => Promise<void>
  sendPayment: (plan: Plan) => Promise<{ success: boolean; txHash?: string; error?: string }>
  isConnecting: boolean
}

const WalletContext = createContext<WalletContextType | undefined>(undefined)

// Static wallet address for receiving payments
const RECIPIENT_ADDRESS = '0x3cB6993b9A70c07E189a3848218D6B04D01A337f' as const

// Available plans
export const PLANS: Plan[] = [
  {
    id: 'starter',
    name: 'Starter',
    description: 'Perfect for getting started',
    price: 0.1,
    credits: 100,
    features: ['Basic AI chat', 'Code generation', 'Email support'],
    currency: 'FLOW'
  },
  {
    id: 'pro',
    name: 'Pro',
    description: 'For professional developers',
    price: 0.5,
    credits: 1000,
    features: ['Advanced AI chat', 'Custom contracts', 'Priority support', 'API access'],
    currency: 'FLOW',
    popular: true
  },
  {
    id: 'enterprise',
    name: 'Enterprise',
    description: 'For teams and organizations',
    price: 2.0,
    credits: 10000,
    features: ['Unlimited AI chat', 'Custom contracts', '24/7 support', 'API access'],
    currency: 'FLOW'
  }
]

export function WalletProvider({ children }: { children: ReactNode }) {
  const [wallet, setWallet] = useState<WalletState>({
    address: null,
    chainId: null,
    isConnected: false,
    balance: null
  })

  const connect = () => {
    console.warn('Web3 functionality temporarily disabled - please refresh the page')
  }

  const disconnect = () => {
    setWallet({
      address: null,
      chainId: null,
      isConnected: false,
      balance: null
    })
  }

  const switchToFlowEVM = async () => {
    console.warn('Web3 functionality temporarily disabled')
  }

  const sendPayment = async (plan: Plan): Promise<{ success: boolean; txHash?: string; error?: string }> => {
    return { success: false, error: 'Web3 functionality temporarily disabled' }
  }

  return (
    <WalletContext.Provider value={{
      wallet,
      connect,
      disconnect,
      switchToFlowEVM,
      sendPayment,
      isConnecting: false
    }}>
      {children}
    </WalletContext.Provider>
  )
}

export function useWallet() {
  const context = useContext(WalletContext)
  if (context === undefined) {
    throw new Error('useWallet must be used within a WalletProvider')
  }
  return context
}

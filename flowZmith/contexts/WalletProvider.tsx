'use client'

import { createContext, useContext, useEffect, useState, ReactNode } from 'react'
import { WalletState, Plan } from '@/lib/web3/types'

// Check if we're in browser environment
const isBrowser = typeof window !== 'undefined'

// Dynamic imports for web3 dependencies
let wagmiAdapter: any = null
let flowEVM: any = null
let useAccount: any = null
let useBalance: any = null
let useSwitchChain: any = null
let useDisconnect: any = null

// Load web3 dependencies only in browser
if (isBrowser) {
  try {
    const wagmiModule = require('wagmi')
    const web3Config = require('@/lib/web3/config')
    
    useAccount = wagmiModule.useAccount
    useBalance = wagmiModule.useBalance
    useSwitchChain = wagmiModule.useSwitchChain
    useDisconnect = wagmiModule.useDisconnect
    wagmiAdapter = web3Config.wagmiAdapter
    flowEVM = web3Config.flowEVM
  } catch (error) {
    console.warn('Failed to load web3 dependencies:', error)
  }
}

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
    description: 'Perfect for small projects',
    price: 10,
    credits: 100,
    currency: 'FLOW',
    features: ['100 AI generations', 'Basic contract templates', 'Email support']
  },
  {
    id: 'pro',
    name: 'Professional',
    description: 'For active developers',
    price: 25,
    credits: 300,
    currency: 'FLOW',
    features: ['300 AI generations', 'Advanced templates', 'Priority support', 'Code optimization']
  },
  {
    id: 'enterprise',
    name: 'Enterprise',
    description: 'For large teams',
    price: 50,
    credits: 1000,
    currency: 'FLOW',
    features: ['1000 AI generations', 'Custom contracts', '24/7 support', 'API access'],
    popular: true
  }
]

export function WalletProvider({ children }: { children: ReactNode }) {
  // Use wagmi hooks only if available
  const accountResult = (isBrowser && useAccount) ? useAccount() : { address: null, chainId: null, isConnected: false, connector: null, isConnecting: false }
  const { address, chainId, isConnected, connector, isConnecting: wagmiIsConnecting } = accountResult
  
  const balanceResult = (isBrowser && useBalance && flowEVM) ? useBalance({
    address,
    chainId: flowEVM.id
  }) : { data: null }
  const { data: balance } = balanceResult

  // Extract only serializable properties from balance
  const balanceFormatted = balance?.formatted || null
  const switchChainResult = (isBrowser && useSwitchChain) ? useSwitchChain() : { switchChain: () => Promise.resolve() }
  const { switchChain } = switchChainResult
  const disconnectResult = (isBrowser && useDisconnect) ? useDisconnect() : { disconnect: () => {} }
  const { disconnect } = disconnectResult

  const [wallet, setWallet] = useState<WalletState>({
    address: null,
    chainId: null,
    isConnected: false,
    balance: null
  })

  useEffect(() => {
    setWallet({
      address: address || null,
      chainId: chainId || null,
      isConnected,
      balance: balanceFormatted
    })
  }, [address, chainId, isConnected, balanceFormatted])

  const connect = () => {
    if (isBrowser && wagmiAdapter && wagmiAdapter.openConnectModal) {
      wagmiAdapter.openConnectModal()
    } else {
      console.warn('Web3 adapter not available')
    }
  }

  const switchToFlowEVM = async () => {
    try {
      if (switchChain && flowEVM) {
        await switchChain({ chainId: flowEVM.id })
      } else {
        throw new Error('Switch chain not available')
      }
    } catch (error) {
      console.error('Failed to switch to Flow EVM:', error)
      throw error
    }
  }

  const sendPayment = async (plan: Plan): Promise<{ success: boolean; txHash?: string; error?: string }> => {
    if (!wallet.address || !wallet.isConnected) {
      return { success: false, error: 'Wallet not connected' }
    }

    if (flowEVM && wallet.chainId !== flowEVM.id) {
      try {
        await switchToFlowEVM()
      } catch (error) {
        return { success: false, error: 'Failed to switch to Flow EVM network' }
      }
    }

    try {
      // Send transaction using wagmi
      if (isBrowser && wagmiAdapter?.walletClient) {
        const txHash = await wagmiAdapter.walletClient.sendTransaction({
          to: RECIPIENT_ADDRESS,
          value: BigInt(plan.price * 1e18), // Convert FLOW to wei
          chainId: flowEVM?.id || 747
        })

        return { success: true, txHash }
      } else {
        return { success: false, error: 'Wallet client not available' }
      }
    } catch (error) {
      console.error('Payment failed:', error)
      return { success: false, error: 'Transaction failed' }
    }
  }

  return (
    <WalletContext.Provider value={{
      wallet,
      connect,
      disconnect: () => disconnect(),
      switchToFlowEVM,
      sendPayment,
      isConnecting: wagmiIsConnecting
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
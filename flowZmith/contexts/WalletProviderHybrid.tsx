'use client'

import { createContext, useContext, useEffect, useState, ReactNode } from 'react'
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
  const [isConnecting, setIsConnecting] = useState(false)
  const [web3Available, setWeb3Available] = useState(false)

  // Check if web3 is available
  useEffect(() => {
    const checkWeb3 = async () => {
      try {
        // Check if we're in browser and have web3
        if (typeof window !== 'undefined' && window.ethereum) {
          setWeb3Available(true)
        }
      } catch (error) {
        console.warn('Web3 not available:', error)
        setWeb3Available(false)
      }
    }
    
    checkWeb3()
  }, [])

  const connect = async () => {
    if (!web3Available) {
      // Try to use the web3 modal if available
      try {
        const { wagmiAdapter } = await import('@/lib/web3/config')
        if (wagmiAdapter && wagmiAdapter.openConnectModal) {
          wagmiAdapter.openConnectModal()
          return
        }
      } catch (error) {
        console.warn('Failed to load web3 adapter:', error)
      }
      
      // Fallback: Show instructions
      alert('Please install a Web3 wallet like MetaMask to connect your wallet.')
      return
    }

    setIsConnecting(true)
    
    try {
      // Use MetaMask or other injected wallet
      if (window.ethereum) {
        const accounts = await window.ethereum.request({ 
          method: 'eth_requestAccounts' 
        })
        
        if (accounts.length > 0) {
          const address = accounts[0]
          const chainId = await window.ethereum.request({ 
            method: 'eth_chainId' 
          })
          
          setWallet({
            address,
            chainId: parseInt(chainId, 16),
            isConnected: true,
            balance: '0.0' // We'll fetch this separately
          })
        }
      }
    } catch (error) {
      console.error('Failed to connect wallet:', error)
      alert('Failed to connect wallet. Please try again.')
    } finally {
      setIsConnecting(false)
    }
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
    if (!web3Available || !window.ethereum) {
      throw new Error('Web3 not available')
    }

    try {
      await window.ethereum.request({
        method: 'wallet_switchEthereumChain',
        params: [{ chainId: '0x2EB' }], // 747 in hex
      })
    } catch (error) {
      // If the chain doesn't exist, try to add it
      try {
        await window.ethereum.request({
          method: 'wallet_addEthereumChain',
          params: [{
            chainId: '0x2EB',
            chainName: 'Flow EVM',
            nativeCurrency: {
              name: 'Flow',
              symbol: 'FLOW',
              decimals: 18,
            },
            rpcUrls: ['https://mainnet.evm.nodes.onflow.org'],
            blockExplorerUrls: ['https://evm.flowscan.io'],
          }],
        })
      } catch (addError) {
        console.error('Failed to add Flow EVM chain:', addError)
        throw addError
      }
    }
  }

  const sendPayment = async (plan: Plan): Promise<{ success: boolean; txHash?: string; error?: string }> => {
    if (!wallet.address || !wallet.isConnected) {
      return { success: false, error: 'Wallet not connected' }
    }

    if (!web3Available || !window.ethereum) {
      return { success: false, error: 'Web3 not available' }
    }

    try {
      // Switch to Flow EVM if needed
      if (wallet.chainId !== 747) {
        await switchToFlowEVM()
      }

      // Send transaction
      const txHash = await window.ethereum.request({
        method: 'eth_sendTransaction',
        params: [{
          from: wallet.address,
          to: RECIPIENT_ADDRESS,
          value: `0x${(plan.price * 1e18).toString(16)}`, // Convert to hex
        }],
      })

      return { success: true, txHash }
    } catch (error) {
      console.error('Payment failed:', error)
      return { success: false, error: 'Transaction failed' }
    }
  }

  return (
    <WalletContext.Provider value={{
      wallet,
      connect,
      disconnect,
      switchToFlowEVM,
      sendPayment,
      isConnecting
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

// Extend Window interface for TypeScript
declare global {
  interface Window {
    ethereum?: {
      request: (args: { method: string; params?: any[] }) => Promise<any>
      on: (event: string, callback: (...args: any[]) => void) => void
      removeListener: (event: string, callback: (...args: any[]) => void) => void
    }
  }
}

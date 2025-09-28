import { Chain } from 'viem'

export interface FlowEVMNetwork extends Chain {
  id: 747
  name: 'Flow EVM'
  nativeCurrency: {
    decimals: 18
    name: 'Flow'
    symbol: 'FLOW'
  }
  rpcUrls: {
    default: {
      http: ['https://mainnet.evm.nodes.onflow.org']
    }
  }
  blockExplorers: {
    default: {
      name: 'Flow EVM Explorer'
      url: 'https://evm.flowscan.io'
    }
  }
}

export interface PaymentData {
  amount: string
  recipient: string
  chainId: number
  tokenAddress?: string
}

export interface Plan {
  id: string
  name: string
  description: string
  price: number
  credits: number
  features: string[]
  popular?: boolean
  currency: 'FLOW'
}

export interface WalletState {
  address: string | null
  chainId: number | null
  isConnected: boolean
  balance: string | null
}
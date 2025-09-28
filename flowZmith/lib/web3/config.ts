import { cookieStorage, createStorage, http } from '@wagmi/core'
import { WagmiAdapter } from '@reown/appkit-adapter-wagmi'
import { mainnet, arbitrum, polygon } from '@reown/appkit/networks'
import { createAppKit } from '@reown/appkit/react'

// Get projectId from environment variables
export const projectId = process.env.NEXT_PUBLIC_REOWN_PROJECT_ID || 'ff7e4c6da87929d965ceb31b6a72924c'

if (!projectId) {
  throw new Error('Project ID is not defined')
}

// Flow EVM Network Configuration
const flowEVM = {
  id: 747,
  name: 'Flow EVM',
  nativeCurrency: {
    decimals: 18,
    name: 'Flow',
    symbol: 'FLOW',
  },
  rpcUrls: {
    default: {
      http: ['https://mainnet.evm.nodes.onflow.org'],
    },
  },
  blockExplorers: {
    default: {
      name: 'Flow EVM Explorer',
      url: 'https://evm.flowscan.io',
    },
  },
  contracts: {
    multicall3: {
      address: '0xca11bde05977b3631167028862be2a173976ca11' as `0x${string}`,
      blockCreated: 25770160,
    },
  },
}

export const networks = [mainnet, arbitrum, polygon, flowEVM]

// Set up the Wagmi Adapter (Config)
export const wagmiAdapter = new WagmiAdapter({
  storage: createStorage({
    storage: cookieStorage
  }),
  ssr: true,
  projectId,
  networks
})

export const config = wagmiAdapter.wagmiConfig

// Create metadata
const metadata = {
  name: 'Smart Contract AI Builder',
  description: 'AI-powered smart contract generation platform',
  url: 'https://smart-contract-ai-builder.vercel.app',
  icons: ['https://avatars.githubusercontent.com/u/17922810']
}

// Create the modal
const modal = createAppKit({
  adapters: [wagmiAdapter],
  projectId,
  networks: [mainnet, arbitrum, polygon, flowEVM],
  defaultNetwork: mainnet,
  metadata: metadata,
  features: {
    analytics: true // Optional - defaults to your Cloud configuration
  }
})

// Export the modal and flowEVM
export { modal, flowEVM }
export type { FlowEVMNetwork } from './types'
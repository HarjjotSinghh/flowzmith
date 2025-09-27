// Fallback configuration for web3 when dependencies fail to load
export const fallbackWagmiAdapter = {
  openConnectModal: () => {
    console.warn('Web3 adapter not available - please refresh the page')
  },
  walletClient: null
}

export const fallbackFlowEVM = {
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
}

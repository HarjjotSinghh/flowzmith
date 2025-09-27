# WalletManager2 MCP Server

Generated MCP server for the WalletManager2 smart contract.

## Contract Information

- **Contract Name**: WalletManager2
- **Contract Address**: 0x01
- **Network**: testnet
- **Generated**: 2025-09-27 13:12:39

## Description

MCP server providing tools to interact with the WalletManager2 smart contract.

## Available Tools

### Contract Functions

#### `call_getAddress`
- **Access Level**: all
- **Return Type**: Address
- **View Function**: No


#### `call_isConnected`
- **Access Level**: all
- **Return Type**: Bool
- **View Function**: No


#### `call_connect`
- **Access Level**: all
- **Return Type**: Void
- **View Function**: No


#### `call_disconnect`
- **Access Level**: all
- **Return Type**: Void
- **View Function**: No


#### `call_addConnector`
Function to add a new connector
- **Access Level**: all
- **Return Type**: Void
- **View Function**: No
- **Parameters**:
  - `id`: String
  - `name`: String


#### `call_removeConnector`
Function to remove a connector
- **Access Level**: all
- **Return Type**: Void
- **View Function**: No
- **Parameters**:
  - `id`: String


#### `call_createWallet`
Function to create a new wallet
- **Access Level**: all
- **Return Type**: Capability<&Wallet>
- **View Function**: No
- **Parameters**:
  - `address`: Address


#### `call_getWalletCapability`
Function to get a wallet capability
- **Access Level**: all
- **Return Type**: Capability<&Wallet>
- **View Function**: No
- **Parameters**:
  - `address`: Address


#### `call_connectWallet`
Function to connect a wallet
- **Access Level**: all
- **Return Type**: Void
- **View Function**: No
- **Parameters**:
  - `address`: Address


#### `call_disconnectWallet`
Function to disconnect a wallet
- **Access Level**: all
- **Return Type**: Void
- **View Function**: No
- **Parameters**:
  - `address`: Address


#### `call_main`
Example script to get a wallet capability
- **Access Level**: all
- **Return Type**: Capability<&WalletManager2.Wallet>
- **View Function**: Yes
- **Parameters**:
  - `address`: Address


### Contract Events

#### `WalletConnected`
Events
- **Parameters**:
  - `address`: Address


#### `WalletDisconnected`
- **Parameters**:
  - `address`: Address


#### `ConnectorAdded`
- **Parameters**:
  - `connectorId`: String


#### `ConnectorRemoved`
- **Parameters**:
  - `connectorId`: String


### General Tools

#### `view_contract_info`
Get general information about the contract.

#### `view_contract_code`
View the contract source code.

#### `get_contract_events`
Get recent events emitted by the contract.

## Usage

### Starting the Server

```bash
python walletmanager2_mcp_server.py
```

### Using with Claude Desktop

Add the following to your Claude Desktop configuration:

```json
{
  "mcpServers": {
    "walletmanager2_mcp": {
      "command": "python",
      "args": [
        "walletmanager2_mcp_server.py"
      ],
      "env": {
        "CONTRACT_ADDRESS": "0x01",
        "NETWORK": "testnet"
      }
    }
  }
}
```

### Example Client Usage

```python
from walletmanager2_mcp_client import ContractMCPClient

async def main():
    client = ContractMCPClient()
    await client.connect()
    
    # View contract info
    info = await client.view_contract_info()
    print(info)
    
    # Call contract functions
    # (Add specific examples based on your contract)
    
    await client.disconnect()
```

## Requirements

- Python 3.8+
- mcp package
- flow-cli (for Flow blockchain interaction)

## Installation

```bash
pip install mcp
# Install Flow CLI: https://developers.flow.com/tools/flow-cli/install
```

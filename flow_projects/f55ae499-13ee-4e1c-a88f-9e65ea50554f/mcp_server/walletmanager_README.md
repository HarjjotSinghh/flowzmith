# WalletManager MCP Server

Generated MCP server for the WalletManager smart contract.

## Contract Information

- **Contract Name**: WalletManager
- **Contract Address**: 0x01
- **Network**: emulator
- **Generated**: 2025-09-27 13:08:05

## Description

MCP server providing tools to interact with the WalletManager smart contract.

## Available Tools

### Contract Functions

#### `call_withdraw`
- **Access Level**: all
- **Return Type**: @Token
- **View Function**: No
- **Parameters**:
  - `amount`: UFix64


#### `call_deposit`
- **Access Level**: all
- **Return Type**: Void
- **View Function**: No
- **Parameters**:
  - `withdraw`: @Token


#### `call_getBalance`
- **Access Level**: all
- **Return Type**: UFix64
- **View Function**: No


#### `call_getID`
- **Access Level**: all
- **Return Type**: UInt64
- **View Function**: No


#### `call_createWallet`
Function to create a new wallet
- **Access Level**: all
- **Return Type**: UInt64
- **View Function**: No


#### `call_getWalletCapability`
Function to get a wallet capability
- **Access Level**: all
- **Return Type**: Capability<&Wallet>
- **View Function**: No
- **Parameters**:
  - `walletID`: UInt64


#### `call_updateWalletBalance`
Function to update a wallet balance
- **Access Level**: all
- **Return Type**: Void
- **View Function**: No
- **Parameters**:
  - `walletID`: UInt64
  - `newBalance`: UFix64


#### `call_deleteWallet`
Function to delete a wallet
- **Access Level**: all
- **Return Type**: Void
- **View Function**: No
- **Parameters**:
  - `walletID`: UInt64


#### `call_main`
Example script to get a wallet balance
- **Access Level**: all
- **Return Type**: UFix64
- **View Function**: No
- **Parameters**:
  - `account`: Address
  - `walletID`: UInt64


### Contract Events

#### `WalletCreated`
Events
- **Parameters**:
  - `address`: Address
  - `walletID`: UInt64


#### `WalletUpdated`
- **Parameters**:
  - `address`: Address
  - `walletID`: UInt64
  - `newBalance`: UFix64


#### `WalletDeleted`
- **Parameters**:
  - `address`: Address
  - `walletID`: UInt64


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
python walletmanager_mcp_server.py
```

### Using with Claude Desktop

Add the following to your Claude Desktop configuration:

```json
{
  "mcpServers": {
    "walletmanager_mcp": {
      "command": "python",
      "args": [
        "walletmanager_mcp_server.py"
      ],
      "env": {
        "CONTRACT_ADDRESS": "0x01",
        "NETWORK": "emulator"
      }
    }
  }
}
```

### Example Client Usage

```python
from walletmanager_mcp_client import ContractMCPClient

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

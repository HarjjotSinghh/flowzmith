# TestNew MCP Server

Generated MCP server for the TestNew smart contract.

## Contract Information

- **Contract Name**: TestNew
- **Contract Address**: 0x01
- **Network**: testnet
- **Generated**: 2025-09-27 12:37:30

## Description

TestNew - Generated Smart Contract
Contract Type: Custom
Network: testnet

## Available Tools

### Contract Functions

### Contract Events

#### `ContractInitialized`
Events


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
python testnew_mcp_server.py
```

### Using with Claude Desktop

Add the following to your Claude Desktop configuration:

```json
{
  "mcpServers": {
    "testnew_mcp": {
      "command": "python",
      "args": [
        "testnew_mcp_server.py"
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
from testnew_mcp_client import ContractMCPClient

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

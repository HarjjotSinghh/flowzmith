# UnknownContract MCP Server

Generated MCP server for the UnknownContract smart contract.

## Contract Information

- **Contract Name**: UnknownContract
- **Contract Address**: 0x01
- **Network**: emulator
- **Generated**: 2025-09-27 13:33:24

## Description

MCP server providing tools to interact with the UnknownContract smart contract.

## Available Tools

### Contract Functions

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
python unknowncontract_mcp_server.py
```

### Using with Claude Desktop

Add the following to your Claude Desktop configuration:

```json
{
  "mcpServers": {
    "unknowncontract_mcp": {
      "command": "python",
      "args": [
        "unknowncontract_mcp_server.py"
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
from unknowncontract_mcp_client import ContractMCPClient

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

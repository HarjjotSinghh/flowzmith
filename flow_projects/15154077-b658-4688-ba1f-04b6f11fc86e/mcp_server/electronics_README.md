# Electronics MCP Server

Generated MCP server for the Electronics smart contract.

## Contract Information

- **Contract Name**: Electronics
- **Contract Address**: 0x01
- **Network**: emulator
- **Generated**: 2025-09-27 13:50:41

## Description

MCP server providing tools to interact with the Electronics smart contract.

## Available Tools

### Contract Functions

#### `call_addDevice`
Add a device to the collection
- **Access Level**: all
- **Return Type**: Void
- **View Function**: No
- **Parameters**:
  - `device`: ElectronicDevice


#### `call_removeDevice`
Remove a device from the collection
- **Access Level**: all
- **Return Type**: ElectronicDevice?
- **View Function**: No
- **Parameters**:
  - `id`: UInt64


#### `call_getDevice`
Get a device from the collection
- **Access Level**: all
- **Return Type**: ElectronicDevice?
- **View Function**: No
- **Parameters**:
  - `id`: UInt64


### Contract Events

#### `DeviceAdded`
Event emitted when a device is added to a collection
- **Parameters**:
  - `deviceId`: UInt64
  - `owner`: Address


#### `DeviceRemoved`
Event emitted when a device is removed from a collection
- **Parameters**:
  - `deviceId`: UInt64
  - `owner`: Address


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
python electronics_mcp_server.py
```

### Using with Claude Desktop

Add the following to your Claude Desktop configuration:

```json
{
  "mcpServers": {
    "electronics_mcp": {
      "command": "python",
      "args": [
        "electronics_mcp_server.py"
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
from electronics_mcp_client import ContractMCPClient

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

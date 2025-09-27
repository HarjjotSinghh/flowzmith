# NewTest MCP Server

Generated MCP server for the NewTest smart contract.

## Contract Information

- **Contract Name**: NewTest
- **Contract Address**: 0x01
- **Network**: testnet
- **Generated**: 2025-09-27 12:54:08

## Description

MCP server providing tools to interact with the NewTest smart contract.

## Available Tools

### Contract Functions

#### `call_updateStatus`
- **Access Level**: all
- **Return Type**: Void
- **View Function**: No
- **Parameters**:
  - `newStatus`: String


#### `call_updateDescription`
- **Access Level**: all
- **Return Type**: Void
- **View Function**: No
- **Parameters**:
  - `newDescription`: String


#### `call_getTest`
- **Access Level**: all
- **Return Type**: Test?
- **View Function**: No
- **Parameters**:
  - `id`: UInt64


#### `call_createTest`
- **Access Level**: all
- **Return Type**: Void
- **View Function**: No
- **Parameters**:
  - `description`: String


#### `call_updateTestStatus`
- **Access Level**: all
- **Return Type**: Void
- **View Function**: No
- **Parameters**:
  - `id`: UInt64
  - `newStatus`: String


#### `call_deleteTest`
- **Access Level**: all
- **Return Type**: Void
- **View Function**: No
- **Parameters**:
  - `id`: UInt64


#### `call_createTestCollection`
Public functions
- **Access Level**: all
- **Return Type**: @TestCollection
- **View Function**: No


#### `call_main`
Example transaction to create a new TestCollection

transaction {
prepare(signer: auth(Storage) &Account) {
let collection <- NewTest.createTestCollection()
signer.save(<-collection, to: /storage/TestCollection)
}
}
Example transaction to create a new Test

transaction {
prepare(signer: auth(Storage) &Account) {
let collection = signer.borrow<&NewTest.TestCollection>(from: /storage/TestCollection)
?? panic("Could not borrow reference to TestCollection")
collection.createTest(description: "New Test Description")
}
}
Example script to read a Test

- **Access Level**: all
- **Return Type**: String?
- **View Function**: No
- **Parameters**:
  - `account`: Address


### Contract Events

#### `TestCreated`
Events
- **Parameters**:
  - `testId`: UInt64


#### `TestUpdated`
- **Parameters**:
  - `testId`: UInt64
  - `newStatus`: String


#### `TestDeleted`
- **Parameters**:
  - `testId`: UInt64


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
python newtest_mcp_server.py
```

### Using with Claude Desktop

Add the following to your Claude Desktop configuration:

```json
{
  "mcpServers": {
    "newtest_mcp": {
      "command": "python",
      "args": [
        "newtest_mcp_server.py"
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
from newtest_mcp_client import ContractMCPClient

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

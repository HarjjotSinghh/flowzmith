# SoftwareTest MCP Server

Generated MCP server for the SoftwareTest smart contract.

## Contract Information

- **Contract Name**: SoftwareTest
- **Contract Address**: 0x01
- **Network**: testnet
- **Generated**: 2025-09-27 13:03:54

## Description

MCP server providing tools to interact with the SoftwareTest smart contract.

## Available Tools

### Contract Functions

#### `call_updateTestName`
- **Access Level**: all
- **Return Type**: Void
- **View Function**: No
- **Parameters**:
  - `newName`: String


#### `call_updateTestStatus`
- **Access Level**: all
- **Return Type**: Void
- **View Function**: No
- **Parameters**:
  - `newStatus`: Bool


#### `call_addTest`
Function to add a new test
- **Access Level**: all
- **Return Type**: Void
- **View Function**: No
- **Parameters**:
  - `test`: Test


#### `call_removeTest`
Function to remove a test
- **Access Level**: all
- **Return Type**: Test?
- **View Function**: No
- **Parameters**:
  - `testID`: UInt64


#### `call_getTest`
Function to get a test
- **Access Level**: all
- **Return Type**: &Test?
- **View Function**: No
- **Parameters**:
  - `testID`: UInt64


#### `call_createTestCollection`
Function to create a new test collection
- **Access Level**: all
- **Return Type**: @TestCollection
- **View Function**: No


#### `call_main`
Example transaction to create a new test collection
transaction {
prepare(signer: AuthAccount) {
let collection <- SoftwareTest.createTestCollection()
signer.save(<-collection, to: /storage/TestCollection)
let cap = signer.link<&SoftwareTest.TestCollection>(/public/TestCollection, target: /storage/TestCollection)
log(cap)
}
}
Example transaction to add a new test
transaction(testName: String) {
prepare(signer: AuthAccount) {
let collectionRef = signer.borrow<&SoftwareTest.TestCollection>(from: /storage/TestCollection)
?? panic("Could not borrow reference to TestCollection")
let test <- create SoftwareTest.Test(testID: 1, testName: testName)
collectionRef.addTest(test: <-test)
}
}
Example script to get a test
- **Access Level**: all
- **Return Type**: String?
- **View Function**: No
- **Parameters**:
  - `testID`: UInt64
  - `address`: Address


### Contract Events

#### `TestCreated`
Define events
- **Parameters**:
  - `testID`: UInt64
  - `testName`: String


#### `TestUpdated`
- **Parameters**:
  - `testID`: UInt64
  - `testName`: String


#### `TestDeleted`
- **Parameters**:
  - `testID`: UInt64


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
python softwaretest_mcp_server.py
```

### Using with Claude Desktop

Add the following to your Claude Desktop configuration:

```json
{
  "mcpServers": {
    "softwaretest_mcp": {
      "command": "python",
      "args": [
        "softwaretest_mcp_server.py"
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
from softwaretest_mcp_client import ContractMCPClient

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

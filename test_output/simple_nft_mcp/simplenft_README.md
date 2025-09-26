# SimpleNFT MCP Server

Generated MCP server for the SimpleNFT smart contract.

## Contract Information

- **Contract Name**: SimpleNFT
- **Contract Address**: 0x1234567890abcdef
- **Network**: testnet
- **Generated**: 2025-09-27 04:51:25

## Description

SimpleNFT.cdc - A basic NFT contract for testing MCP generation
/ SimpleNFT contract for testing MCP server generation
/ This contract demonstrates basic NFT functionality with events and view functions

## Available Tools

### Contract Functions

#### `call_getViews`
/ Function that returns all the Metadata Views implemented by a Non Fungible Token
- **Access Level**: all
- **Return Type**: [Type]
- **View Function**: Yes


#### `call_resolveView`
/ Function that resolves a metadata view for this token
- **Access Level**: all
- **Return Type**: AnyStruct?
- **View Function**: No
- **Parameters**:
  - `view`: Type (label: _)


#### `call_getIDs`
- **Access Level**: all
- **Return Type**: [UInt64]
        pub fun borrowNFT(id: UInt64): &NonFungibleToken.NFT
        pub fun borrowSimpleNFT(id: UInt64): &SimpleNFT.NFT?
- **View Function**: Yes


#### `call_withdraw`
/ Removes an NFT from the collection and moves it to the caller
- **Access Level**: all
- **Return Type**: @NonFungibleToken.NFT
- **View Function**: No
- **Parameters**:
  - `withdrawID`: UInt64


#### `call_deposit`
/ Adds an NFT to the collections dictionary and adds the ID to the id array
- **Access Level**: all
- **Return Type**: Void
- **View Function**: No
- **Parameters**:
  - `token`: @NonFungibleToken.NFT


#### `call_borrowNFT`
/ Gets a reference to an NFT in the collection so that
/ the caller can read its metadata and call its methods
- **Access Level**: all
- **Return Type**: &NonFungibleToken.NFT
- **View Function**: No
- **Parameters**:
  - `id`: UInt64


#### `call_borrowSimpleNFT`
/ Gets a reference to an NFT in the collection as a SimpleNFT,
/ This is safe as there are no functions that can be called on the SimpleNFT
- **Access Level**: all
- **Return Type**: &SimpleNFT.NFT?
- **View Function**: No
- **Parameters**:
  - `id`: UInt64


#### `call_borrowViewResolver`
/ Gets a reference to the NFT only conforming to the `{MetadataViews.Resolver}`
/ interface so that the caller can retrieve the views that the NFT
/ is implementing and resolve them
- **Access Level**: all
- **Return Type**: &AnyResource
- **View Function**: Yes
- **Parameters**:
  - `id`: UInt64


#### `call_createEmptyCollection`
/ Allows anyone to create a new empty collection
- **Access Level**: all
- **Return Type**: @NonFungibleToken.Collection
- **View Function**: No


#### `call_mintNFT`
/ Mints a new NFT with a new ID and deposit it in the
/ recipients collection using their collection reference
- **Access Level**: all
- **Return Type**: UInt64
- **View Function**: Yes
- **Parameters**:
  - `recipient`: &{NonFungibleToken.CollectionPublic}
  - `metadata`: {String: String}


#### `call_getTotalSupply`
/ Get the total supply of NFTs
- **Access Level**: all
- **Return Type**: UInt64
- **View Function**: No


#### `call_getContractInfo`
/ Get contract information
- **Access Level**: all
- **Return Type**: Void
- **View Function**: Yes


### Contract Events

#### `ContractInitialized`
/ Event emitted when the contract is initialized


#### `Withdraw`
/ Event emitted when an NFT is withdrawn from a collection
- **Parameters**:
  - `id`: UInt64
  - `from`: Address?


#### `Deposit`
/ Event emitted when an NFT is deposited to a collection
- **Parameters**:
  - `id`: UInt64
  - `to`: Address?


#### `Minted`
/ Event emitted when an NFT is minted
- **Parameters**:
  - `id`: UInt64
  - `recipient`: Address
  - `metadata`: {String: String}


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
python simplenft_mcp_server.py
```

### Using with Claude Desktop

Add the following to your Claude Desktop configuration:

```json
{
  "mcpServers": {
    "simplenft_mcp": {
      "command": "python",
      "args": [
        "simplenft_mcp_server.py"
      ],
      "env": {
        "CONTRACT_ADDRESS": "0x1234567890abcdef",
        "NETWORK": "testnet"
      }
    }
  }
}
```

### Example Client Usage

```python
from simplenft_mcp_client import ContractMCPClient

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

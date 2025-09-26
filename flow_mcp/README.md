# Flow MCP Server

A Model Context Protocol (MCP) server for interacting with Flow blockchain smart contracts, accounts, and transactions using the Flow CLI.

## Features

- **Contract Operations**: Call functions, view contracts, deploy contracts
- **Account Management**: View account details, check balances, list accounts
- **Transaction Explorer**: View transactions, list recent transactions
- **Flow CLI Integration**: Seamless integration with Flow CLI commands
- **MCP Protocol**: Compatible with MCP clients and Claude Desktop

## Installation

### Prerequisites

- Python 3.8+
- Flow CLI installed and configured
- MCP Python SDK

### Install Dependencies

```bash
pip install -r mcp/requirements.txt
```

### Install Flow CLI

If you don't have Flow CLI installed:

```bash
sh -ci "$(curl -fsSL https://storage.googleapis.com/flow-cli/install.sh)"
```

## Usage

### CLI Integration

The MCP server is integrated into the existing CLI:

```bash
# Use the MCP explorer
python cli.py mcp-explorer

# This provides an interactive menu for exploring Flow blockchain
```

### Standalone MCP Server

Run the MCP server directly:

```bash
python mcp/flow_mcp_server.py

# Or with MCP CLI
uv run mcp dev mcp/flow_mcp_server.py
```

### Claude Desktop Integration

Install the MCP server in Claude Desktop:

```bash
uv run mcp install mcp/flow_mcp_server.py --name "Flow Blockchain"
```

## Available Tools

### Contract Operations

- `call_contract`: Call a function on a smart contract
- `view_contract`: View a deployed smart contract
- `deploy_contract`: Deploy a smart contract

### Account Operations

- `view_account`: View account information
- `list_accounts`: List available accounts
- `get_account_balance`: Get account balance

### Transaction Operations

- `view_transaction`: View transaction details
- `list_transactions`: List recent transactions

## Available Resources

- `flow://contract/{address}/{name}`: Get contract as a resource
- `flow://account/{address}`: Get account as a resource
- `flow://transaction/{tx_id}`: Get transaction as a resource

## Available Prompts

- `analyze_contract_prompt`: Generate prompts for contract analysis

## API Integration

The MCP server provides API endpoints that can be integrated into your existing FastAPI application:

```python
from mcp.api_integration import router

# Add to your FastAPI app
app.include_router(router)
```

Available endpoints:
- `GET /mcp/health` - Health check
- `GET /mcp/accounts` - List accounts
- `GET /mcp/accounts/{address}` - Get account details
- `GET /mcp/accounts/{address}/balance` - Get account balance
- `GET /mcp/contracts/{address}/{name}` - Get contract details
- `POST /mcp/contracts/deploy` - Deploy contract
- `GET /mcp/transactions` - List transactions
- `GET /mcp/transactions/{tx_id}` - Get transaction details
- `POST /mcp/contracts/call` - Call contract function

## Configuration

### Environment Variables

- `FLOW_CONFIG_PATH`: Path to Flow configuration file
- `FLOW_NETWORK`: Default network (emulator, testnet, mainnet)

### Flow CLI Configuration

Make sure your Flow CLI is properly configured with accounts and networks:

```bash
# Check configuration
flow configuration show

# Add account
flow accounts add --name my-account --address 0x... --key 0x...

# Switch network
flow project switch-network emulator
```

## Examples

### Using the CLI Explorer

```bash
python cli.py mcp-explorer
```

This will show:
1. Available accounts
2. Interactive menu for:
   - Viewing account details
   - Viewing contracts
   - Viewing transactions
   - Listing recent transactions

### Calling a Contract Function

```python
from mcp.mcp_client import MCPFlowClient

async def example():
    client = MCPFlowClient()
    await client.connect()

    result = await client.call_contract({
        "network": "emulator",
        "account": "my-account",
        "contract_name": "MyContract",
        "function_name": "myFunction",
        "arguments": ["arg1", "arg2"]
    })

    print(result)
    await client.disconnect()
```

### Viewing Account Details

```python
from mcp.mcp_client import MCPFlowClient

async def example():
    client = MCPFlowClient()
    await client.connect()

    account = await client.view_account("0x1654653399040a61")
    print(account)

    await client.disconnect()
```

## Development

### Running in Development Mode

```bash
uv run mcp dev mcp/flow_mcp_server.py
```

### Testing

```bash
# Test individual tools
python -c "
from mcp.mcp_client import MCPFlowClient
import asyncio

async def test():
    client = MCPFlowClient()
    await client.connect()
    accounts = await client.list_accounts()
    print(accounts)
    await client.disconnect()

asyncio.run(test())
"
```

## Troubleshooting

### Common Issues

1. **Flow CLI not found**: Make sure Flow CLI is installed and in your PATH
2. **Account not found**: Ensure accounts are properly configured in Flow CLI
3. **Network connection**: Check if you can connect to the specified network
4. **MCP server errors**: Check logs for detailed error messages

### Debug Mode

Enable debug logging:

```bash
export FLOW_LOG_LEVEL=debug
python mcp/flow_mcp_server.py
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

MIT License - see LICENSE file for details.
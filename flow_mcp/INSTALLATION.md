# Installation Guide

## Prerequisites

Before installing the Flow MCP Server, ensure you have the following:

### System Requirements
- Python 3.8 or higher
- Flow CLI installed and configured
- Internet connection for downloading dependencies

### Flow CLI Installation

If you haven't installed Flow CLI yet:

```bash
# For macOS
sh -ci "$(curl -fsSL https://storage.googleapis.com/flow-cli/install.sh)"

# For Linux
sh -ci "$(curl -fsSL https://storage.googleapis.com/flow-cli/install.sh)"

# For Windows (PowerShell)
iex "& { $(irm https://storage.googleapis.com/flow-cli/install.ps1) }"
```

Verify Flow CLI installation:

```bash
flow version
```

## Installation Steps

### 1. Clone or Download the Project

If you're working with the existing project:

```bash
cd /path/to/smart-contract-llm
```

### 2. Install Python Dependencies

```bash
pip install -r mcp/requirements.txt
```

### 3. Configure Flow CLI

Set up your Flow CLI configuration:

```bash
# Initialize Flow project (if needed)
flow project init

# Add accounts for testing
flow accounts add --name emulator-account --address 0x1654653399040a61 --key 0x...

# Configure emulator
flow emulator start
```

### 4. Verify Installation

Test the MCP server:

```bash
python -c "
from mcp.mcp_client import MCPFlowClient
import asyncio

async def test():
    client = MCPFlowClient()
    await client.connect()
    accounts = await client.list_accounts()
    print('MCP server working! Available accounts:', accounts)
    await client.disconnect()

asyncio.run(test())
"
```

## Claude Desktop Integration

### Install MCP Server in Claude Desktop

```bash
uv run mcp install mcp/flow_mcp_server.py --name "Flow Blockchain"
```

### Manual Installation

Add this to your Claude Desktop configuration:

```json
{
  "mcpServers": {
    "flow-blockchain": {
      "command": "python",
      "args": ["/path/to/smart-contract-llm/mcp/flow_mcp_server.py"],
      "env": {}
    }
  }
}
```

## CLI Integration

The MCP server is integrated into the existing CLI. Test it:

```bash
python cli.py mcp-explorer
```

## Troubleshooting

### Common Issues

1. **Flow CLI not found**
   ```bash
   flow version
   # If not found, add Flow CLI to your PATH
   export PATH=$PATH:/path/to/flow/cli
   ```

2. **Python import errors**
   ```bash
   pip install -r mcp/requirements.txt
   ```

3. **MCP server connection issues**
   ```bash
   python mcp/flow_mcp_server.py
   # Check for errors in the console
   ```

4. **Flow emulator not running**
   ```bash
   flow emulator start
   ```

### Debug Mode

Enable detailed logging:

```bash
export FLOW_LOG_LEVEL=debug
export PYTHONPATH=$PYTHONPATH:/path/to/smart-contract-llm
python mcp/flow_mcp_server.py
```

## Configuration Files

### Flow Configuration

Ensure your `flow.json` is properly configured:

```json
{
  "contracts": {},
  "networks": {
    "emulator": {
      "host": "127.0.0.1",
      "port": 3569
    }
  },
  "accounts": {
    "emulator-account": {
      "address": "0x1654653399040a61",
      "key": "0x..."
    }
  },
  "deployments": {}
}
```

### Environment Variables

Create a `.env` file:

```bash
# Flow configuration
FLOW_CONFIG_PATH=./flow.json
FLOW_NETWORK=emulator

# Debugging
FLOW_LOG_LEVEL=info
PYTHONPATH=/path/to/smart-contract-llm
```

## Testing the Installation

### 1. Test CLI Integration

```bash
python cli.py mcp-explorer
```

### 2. Test MCP Server

```bash
uv run mcp dev mcp/flow_mcp_server.py
```

### 3. Test API Integration

```bash
# Start your main API server
python -m uvicorn src.main:app --reload

# Test the MCP endpoints
curl http://localhost:8000/mcp/health
```

### 4. Run Example

```bash
python mcp/examples/example_usage.py
```

## Next Steps

1. **Explore the Features**: Use the CLI explorer to understand available operations
2. **Deploy a Contract**: Try deploying the sample contract
3. **Integrate with Your Project**: Use the MCP client in your existing code
4. **Customize**: Modify the server to add your specific needs

## Support

If you encounter issues:

1. Check the troubleshooting section
2. Verify Flow CLI installation
3. Ensure Python dependencies are installed
4. Test with the example scripts
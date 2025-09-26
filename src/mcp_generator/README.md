# MCP Server Generator for Smart Contracts

This module automatically generates custom Model Context Protocol (MCP) servers for smart contracts, enabling AI agents to interact with blockchain contracts through standardized tools and resources.

## Overview

The MCP Generator analyzes Cadence smart contracts and creates corresponding MCP servers that expose contract functionality through:
- **Tools**: Functions that AI can call to interact with the contract
- **Resources**: Structured data about the contract and its state
- **Configuration**: Ready-to-use Claude Desktop integration

## Features

- 🔍 **Automatic Contract Analysis**: Extracts functions, events, and structures from Cadence contracts
- 🛠️ **Tool Generation**: Creates MCP tools for each contract function
- 📊 **Resource Mapping**: Exposes contract data through MCP resources
- 🤖 **AI Integration**: Uses system prompts for enhanced generation
- ⚙️ **Configuration**: Generates Claude Desktop config files
- 🧪 **Testing**: Includes test clients for validation

## Architecture

```
src/mcp_generator/
├── contract_analyzer.py      # Analyzes Cadence contracts
├── mcp_server_generator.py   # Generates MCP servers
├── system_prompt.py          # AI prompts for generation
├── templates/                # Template files
│   ├── mcp_server_template.py
│   └── mcp_client_template.py
└── README.md                # This file
```

## Usage

### Automatic Generation (via CLI)

When you generate a contract using the CLI, an MCP server is automatically created:

```bash
python cli.py create-contract
```

The MCP server will be generated in the project's `mcp_server/` directory.

### Manual Generation

```python
from src.mcp_generator.mcp_server_generator import MCPServerGenerator

# Initialize generator
generator = MCPServerGenerator()

# Generate MCP server
await generator.generate_mcp_server(
    contract_file="path/to/contract.cdc",
    output_dir="path/to/output",
    contract_name="MyContract",
    contract_address="0x123...",
    network="testnet"
)
```

### AI-Enhanced Generation

```python
# Use AI for enhanced analysis and generation
await generator.generate_mcp_server_with_ai(
    contract_file="path/to/contract.cdc",
    output_dir="path/to/output",
    contract_name="MyContract",
    contract_address="0x123...",
    network="testnet",
    ai_client=your_ai_client  # Optional AI client
)
```

## Generated Files

For each contract, the generator creates:

### 1. `mcp_server.py`
The main MCP server implementation with:
- Contract-specific tools for each function
- Standard tools (view_contract_info, view_contract_code)
- Event querying capabilities
- Error handling and logging

### 2. `mcp_client.py`
A test client for validation:
- Connection management
- Tool testing examples
- Usage demonstrations

### 3. `config.json`
Claude Desktop configuration:
```json
{
  "mcpServers": {
    "MyContract_mcp": {
      "command": "python",
      "args": ["path/to/mcp_server.py"],
      "env": {
        "FLOW_NETWORK": "testnet",
        "CONTRACT_ADDRESS": "0x123..."
      }
    }
  }
}
```

### 4. `README.md`
Documentation including:
- Setup instructions
- Available tools
- Usage examples
- Troubleshooting

## Contract Analysis

The system analyzes contracts to extract:

### Functions
- **View Functions**: Read-only operations → `get_*` tools
- **Transaction Functions**: State-changing operations → `call_*` tools
- Parameters and return types
- Documentation and descriptions

### Events
- Event definitions → `get_*_events` tools
- Event parameters
- Filtering capabilities

### Resources/Structs
- Data structures
- Field definitions
- Type mappings

## Tool Generation Patterns

### View Functions (Read-only)
```python
@mcp.tool()
async def get_total_supply() -> str:
    """Get the total supply of tokens"""
    command = [
        "flow", "scripts", "execute",
        "--network", "testnet",
        "--code", "import MyContract from 0x123; pub fun main(): UFix64 { return MyContract.getTotalSupply() }"
    ]
    result = await run_flow_command(command)
    return json.dumps(result)
```

### Transaction Functions (State-changing)
```python
@mcp.tool()
async def call_transfer(to: str, amount: float) -> str:
    """Transfer tokens to another account"""
    command = [
        "flow", "transactions", "send",
        "--network", "testnet",
        "--code", f"import MyContract from 0x123; transaction {{ execute {{ MyContract.transfer(to: {to}, amount: {amount}) }} }}"
    ]
    result = await run_flow_command(command)
    return json.dumps(result)
```

### Event Queries
```python
@mcp.tool()
async def get_transfer_events(start_block: Optional[int] = None) -> str:
    """Get Transfer events from the contract"""
    command = ["flow", "events", "get", "0x123.MyContract.Transfer"]
    if start_block:
        command.extend(["--start", str(start_block)])
    command.extend(["--network", "testnet"])
    
    result = await run_flow_command(command)
    return json.dumps(result)
```

## Type Mapping

Cadence types are mapped to Python types:

| Cadence Type | Python Type | JSON Schema |
|--------------|-------------|-------------|
| `String` | `str` | `"string"` |
| `Int`, `UInt64` | `int` | `"integer"` |
| `UFix64`, `Fix64` | `float` | `"number"` |
| `Bool` | `bool` | `"boolean"` |
| `Address` | `str` | `"string"` |
| `[Type]` | `List[Type]` | `"array"` |
| `{String: Type}` | `Dict[str, Type]` | `"object"` |
| `Type?` | `Optional[Type]` | `"type \| null"` |

## Integration with Claude Desktop

1. **Copy the generated `config.json`** to your Claude Desktop configuration
2. **Restart Claude Desktop** to load the new MCP server
3. **Test the integration** by asking Claude about your contract

Example Claude interaction:
```
User: "What functions are available in my contract?"
Claude: *uses view_contract_info tool* "Your contract has the following functions: getTotalSupply(), transfer(), getBalance()..."

User: "Check the total supply"
Claude: *uses get_total_supply tool* "The current total supply is 1,000,000 tokens"
```

## System Prompt

The generator uses a comprehensive system prompt that includes:
- MCP concepts and best practices
- Contract analysis guidelines
- Tool generation patterns
- Type mapping rules
- Error handling strategies
- Configuration examples

Access the system prompt:
```python
from src.mcp_generator.system_prompt import get_mcp_generation_system_prompt

prompt = get_mcp_generation_system_prompt()
```

## Error Handling

All generated tools include robust error handling:
- Flow CLI command failures
- Network connectivity issues
- Invalid parameters
- Contract execution errors

Example error response:
```json
{
  "success": false,
  "error": "Contract function not found: invalidFunction",
  "details": "Available functions: getTotalSupply, transfer, getBalance"
}
```

## Testing

Test your generated MCP server:

```python
# Run the test client
python mcp_client.py

# Or test individual tools
from mcp_server import mcp

# Test contract info
info = await mcp.call_tool("view_contract_info", {})
print(info)
```

## Troubleshooting

### Common Issues

1. **Flow CLI not found**
   - Install Flow CLI: `sh -ci "$(curl -fsSL https://storage.googleapis.com/flow-cli/install.sh)"`
   - Ensure it's in your PATH

2. **Network connection errors**
   - Check network configuration
   - Verify contract address
   - Test Flow CLI connectivity: `flow version`

3. **Claude Desktop integration**
   - Verify config.json syntax
   - Check file paths are absolute
   - Restart Claude Desktop after config changes

4. **Tool execution failures**
   - Check contract deployment status
   - Verify function signatures
   - Test with Flow CLI directly

### Debug Mode

Enable debug logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Contributing

To extend the MCP generator:

1. **Add new tool patterns** in `mcp_server_generator.py`
2. **Enhance contract analysis** in `contract_analyzer.py`
3. **Update templates** in `templates/`
4. **Improve system prompts** in `system_prompt.py`

## Examples

See the generated examples in:
- `flow_projects/*/mcp_server/` - Generated MCP servers
- `flow_mcp/` - Reference implementation
- `context/MCP/` - MCP documentation

## License

This module is part of the smart contract LLM project and follows the same license terms.
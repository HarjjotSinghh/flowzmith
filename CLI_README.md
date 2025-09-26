# Smart Contract LLM Builder CLI

A comprehensive command-line interface for the Smart Contract LLM Builder application. Provides step-by-step guided workflows for smart contract creation, deployment, and management.

## Features

- **🚀 Smart Contract Creation**: Interactive contract creation with multiple input methods
- **🔧 Contract Deployment**: Deploy contracts to Flow blockchain with real-time monitoring
- **📚 Documentation Search**: Search and browse documentation with semantic search
- **📊 System Monitoring**: Check system status and view statistics
- **⚡ Real-time Updates**: WebSocket integration for live progress tracking
- **🧙 Guided Wizard**: Complete end-to-end workflow automation

## Installation

1. Ensure Python 3.8+ is installed
2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Quick Start

1. **Setup Environment**:
```bash
python cli.py setup
```

2. **Create a Contract**:
```bash
python cli.py create-contract
```

3. **Deploy Contract**:
```bash
python cli.py deploy-contract
```

4. **Run Complete Wizard**:
```bash
python cli.py wizard
```

## Commands

### Setup & Configuration

#### `setup`
Setup and verify the development environment.
```bash
python cli.py setup
```

#### `status`
Check system status and view statistics.
```bash
python cli.py status
```

### Contract Management

#### `create-contract`
Create a new smart contract with step-by-step guidance.
```bash
python cli.py create-contract
```

**Input Methods Available:**
- Natural Language Description
- Upload CADENCE (.cdc) File
- Upload Solidity (.sol) File
- Paste Contract Code Directly
- Use Template/Example

#### `deploy-contract`
Deploy a smart contract to the blockchain.
```bash
python cli.py deploy-contract
```

#### `list-deployments`
List all contract deployments.
```bash
python cli.py list-deployments
```

### Documentation

#### `search-docs`
Search documentation and knowledge base.
```bash
python cli.py search-docs
```

#### `upload-docs`
Upload documentation to the knowledge base.
```bash
python cli.py upload-docs
```

#### `browse-docs`
Browse documentation by categories.
```bash
python cli.py browse-docs
```

### Workflow Automation

#### `wizard`
Run the complete contract creation wizard.
```bash
python cli.py wizard
```

This wizard guides you through:
1. Environment setup
2. Contract creation
3. Contract deployment (optional)

### System Information

#### `version`
Show CLI version information.
```bash
python cli.py version
```

## Usage Examples

### Creating a Token Contract

```bash
# Start the wizard for complete guidance
python cli.py wizard

# Or create contract directly
python cli.py create-contract

# Follow the prompts:
# 1. Select "Natural Language Description"
# 2. Enter: "I want to create a fungible token contract with minting capabilities"
# 3. Set contract name to "MyToken"
# 4. Choose Token type
# 5. Configure token details (supply, symbol, etc.)
# 6. Review and confirm
```

### Deploying a Contract

```bash
python cli.py deploy-contract

# Follow the prompts:
# 1. Select contract from available contracts
# 2. Choose network (testnet/mainnet)
# 3. Configure gas parameters
# 4. Review deployment summary
# 5. Confirm deployment
```

### Searching Documentation

```bash
python cli.py search-docs

# Enter search query:
# "Flow token contract development"

# View results and:
# - Browse specific documents
# - Export documentation
# - Find related content
```

## Requirements

- Python 3.8 or higher
- Running Smart Contract LLM Builder backend server
- PostgreSQL database connection
- Environment variables configured (`DATABASE_URL`)

## Environment Variables

The CLI requires the following environment variables:

- `DATABASE_URL`: PostgreSQL connection string
- `OPENAI_API_KEY`: OpenAI API key (for AI features)
- `GROQ_API_KEY`: Groq API key (for alternative AI provider)

## Architecture

The CLI is built with:

- **Typer**: Modern CLI framework
- **Rich**: Beautiful terminal formatting
- **aiohttp**: Async HTTP client
- **websockets**: Real-time communication
- **SQLAlchemy**: Database operations

### Module Structure

```
src/cli/
├── __init__.py
├── api_client.py          # HTTP/WebSocket client
├── contract_creator.py    # Contract creation logic
├── deployment_manager.py  # Deployment management
└── doc_search.py         # Documentation search
```

## Real-time Features

The CLI integrates with the backend's WebSocket system to provide:

- **Live Progress Updates**: Real-time contract creation and deployment progress
- **System Notifications**: Live status updates and alerts
- **Operation Streaming**: Continuous output streaming for long-running operations

## Error Handling

The CLI provides comprehensive error handling:

- **Connection Errors**: Clear messages when server is unavailable
- **Validation Errors**: Input validation with helpful feedback
- **API Errors**: Detailed error messages from backend API
- **Database Errors**: Connection and query error handling

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## License

This project is part of the Smart Contract LLM Builder ecosystem.

## Support

For issues and questions:
- Check the main project documentation
- Review existing issues
- Create a new issue with detailed information

---

**Built with ❤️ by [HarjjotSinghh](https://harjot.co) using Typer and Rich**
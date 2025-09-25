# Examples

This directory contains comprehensive examples demonstrating how to use the Smart Contract LLM Builder platform.

## Available Examples

### 1. API Integration Examples
- [Python SDK Examples](./python/) - Complete Python SDK with various use cases
- [JavaScript SDK Examples](./javascript/) - JavaScript/Node.js integration examples
- [cURL Examples](./curl/) - Command-line API usage examples

### 2. Contract Generation Examples
- [Simple NFT Contract](./contracts/simple_nft/) - Basic NFT with mint and transfer
- [Advanced Token Contract](./contracts/advanced_token/) - Fungible token with advanced features
- [Marketplace Contract](./contracts/marketplace/) - NFT marketplace with bidding
- [DAO Contract](./contracts/dao/) - Decentralized autonomous organization
- [Staking Contract](./contracts/staking/) - Token staking with rewards

### 3. Deployment Examples
- [Testnet Deployment](./deployment/testnet/) - Deploy to Flow testnet
- [Mainnet Deployment](./deployment/mainnet/) - Deploy to Flow mainnet
- [Gas Optimization](./deployment/gas_optimization/) - Optimize gas usage
- [Multi-contract Deployment](./deployment/multi_contract/) - Deploy multiple related contracts

### 4. Configuration Examples
- [Flow CLI Setup](./config/flow_cli/) - Configure Flow CLI for development
- [Environment Configuration](./config/environment/) - Set up development environment
- [Database Setup](./config/database/) - Configure PostgreSQL or SQLite
- [Docker Deployment](./config/docker/) - Deploy with Docker containers

### 5. Integration Examples
- [Webhook Integration](./integration/webhooks/) - Set up webhook notifications
- [WebSocket Integration](./integration/websocket/) - Real-time updates via WebSocket
- [Frontend Integration](./integration/frontend/) - React/Vue.js integration examples
- [Testing Framework](./integration/testing/) - Integration testing examples

## Quick Start

### Python Example

```python
from examples.python.smart_contract_client import SmartContractClient

# Initialize client
client = SmartContractClient()

# Login
client.login('user@example.com', 'password')

# Generate NFT contract
result = client.generate_contract(
    description="Create a simple NFT contract with mint and transfer functions",
    network="testnet"
)

# Deploy contract
deployment = client.deploy_contract(
    submission_id=result['data']['submission_id']
)

print(f"Contract deployed at: {deployment['data']['contract_address']}")
```

### JavaScript Example

```javascript
const { SmartContractClient } = require('./examples/javascript');

// Initialize client
const client = new SmartContractClient();

// Login
await client.login('user@example.com', 'password');

// Generate contract
const result = await client.generateContract(
    'Create a simple NFT contract with mint and transfer functions',
    'testnet'
);

// Deploy contract
const deployment = await client.deployContract(
    result.data.submission_id
);

console.log(`Contract deployed at: ${deployment.data.contract_address}`);
```

## Running Examples

### Prerequisites

1. **Install Dependencies**
   ```bash
   # Python examples
   pip install -r examples/python/requirements.txt

   # JavaScript examples
   cd examples/javascript && npm install
   ```

2. **Set Environment Variables**
   ```bash
   export API_BASE_URL="http://localhost:8000/api/v1"
   export API_EMAIL="your-email@example.com"
   export API_PASSWORD="your-password"
   ```

3. **Start the Application**
   ```bash
   # Start the Smart Contract LLM Builder
   python src/main.py
   ```

### Running Specific Examples

#### Python Examples
```bash
# Run basic example
python examples/python/basic_usage.py

# Run contract generation examples
python examples/python/contract_generation.py

# Run deployment examples
python examples/python/deployment.py

# Run all examples
python examples/python/run_all.py
```

#### JavaScript Examples
```bash
# Run basic example
node examples/javascript/basic_usage.js

# Run contract generation examples
node examples/javascript/contract_generation.js

# Run deployment examples
node examples/javascript/deployment.js

# Run all examples
npm run examples
```

#### cURL Examples
```bash
# Make examples executable
chmod +x examples/curl/*.sh

# Run basic example
./examples/curl/basic_usage.sh

# Run contract generation example
./examples/curl/contract_generation.sh

# Run deployment example
./examples/curl/deployment.sh
```

## Example Structure

### API Integration Examples

Each API integration example includes:
- Complete SDK implementation
- Authentication handling
- Error handling and retry logic
- Response parsing and validation
- Configuration management

### Contract Generation Examples

Contract examples demonstrate:
- Natural language descriptions
- Pre-condition and post-condition definitions
- Configuration generation
- Code validation and optimization
- Best practices and patterns

### Deployment Examples

Deployment examples show:
- Network configuration
- Gas estimation and optimization
- Transaction monitoring
- Error handling and recovery
- Verification and testing

### Integration Examples

Integration examples provide:
- WebSocket connection management
- Webhook setup and handling
- Frontend integration patterns
- Testing frameworks and utilities
- Monitoring and logging

## Customizing Examples

### Environment Configuration

Most examples can be configured via environment variables or configuration files:

```python
# Configuration example
config = {
    'base_url': os.getenv('API_BASE_URL', 'http://localhost:8000/api/v1'),
    'email': os.getenv('API_EMAIL'),
    'password': os.getenv('API_PASSWORD'),
    'default_network': 'testnet',
    'timeout': 30,
    'retry_attempts': 3
}
```

### Contract Templates

Customize contract generation templates:

```python
contract_templates = {
    'nft_basic': {
        'description': 'Create a basic NFT contract with standard features',
        'pre_conditions': {'accounts': {'admin': '0x123'}},
        'post_conditions': {'resources': ['NFT', 'Collection']}
    },
    'token_standard': {
        'description': 'Create a fungible token following Flow token standards',
        'pre_conditions': {'total_supply': 1000000},
        'post_conditions': {'events': ['TokensMinted', 'TokensTransferred']}
    }
}
```

## Best Practices

### Error Handling

```python
try:
    result = client.generate_contract(description)
except SmartContractError as e:
    print(f"Contract generation failed: {e}")
    # Handle specific error types
    if e.code == 'INSUFFICIENT_GAS':
        # Retry with higher gas limit
    elif e.code == 'INVALID_INPUT':
        # Validate and retry
except NetworkError as e:
    print(f"Network error: {e}")
    # Implement retry logic
```

### Async Operations

```javascript
// Use async/await for better error handling
async function deployWithRetry(client, submissionId, maxRetries = 3) {
    for (let i = 0; i < maxRetries; i++) {
        try {
            return await client.deployContract(submissionId);
        } catch (error) {
            if (i === maxRetries - 1) throw error;
            await new Promise(resolve => setTimeout(resolve, 1000 * (i + 1)));
        }
    }
}
```

### Configuration Management

```javascript
// Centralized configuration
const config = {
    api: {
        baseUrl: process.env.API_BASE_URL || 'http://localhost:8000/api/v1',
        timeout: parseInt(process.env.API_TIMEOUT) || 30000,
        retries: parseInt(process.env.API_RETRIES) || 3
    },
    contract: {
        defaultNetwork: process.env.DEFAULT_NETWORK || 'testnet',
        gasLimit: parseInt(process.env.DEFAULT_GAS_LIMIT) || 1000
    }
};
```

## Testing Examples

### Unit Tests

```python
import pytest
from examples.python.smart_contract_client import SmartContractClient

def test_contract_generation():
    client = SmartContractClient()
    client.login('test@example.com', 'password')

    result = client.generate_contract('Create a simple token')
    assert result['success'] == True
    assert 'submission_id' in result['data']
```

### Integration Tests

```javascript
describe('Contract Deployment', () => {
    let client;

    beforeAll(async () => {
        client = new SmartContractClient();
        await client.login('test@example.com', 'password');
    });

    test('should deploy contract successfully', async () => {
        const result = await client.generateContract('Simple token');
        const deployment = await client.deployContract(result.data.submission_id);

        expect(deployment.success).toBe(true);
        expect(deployment.data.status).toBe('SUCCESS');
    });
});
```

## Contributing Examples

We welcome community contributions! To add new examples:

1. **Follow the Structure**
   - Use existing directory structure
   - Include comprehensive documentation
   - Add proper error handling

2. **Test Your Examples**
   - Ensure examples work with the latest API
   - Include unit and integration tests
   - Test edge cases and error conditions

3. **Documentation**
   - Include README files for complex examples
   - Add inline code comments
   - Provide usage instructions

4. **Submit Pull Request**
   - Create feature branch
   - Include example in appropriate directory
   - Update main README if needed

## Support

For issues with examples:
1. Check the troubleshooting section
2. Review existing issues
3. Create new issue with:
   - Example name
   - Error description
   - Expected vs actual behavior
   - Environment information

Happy coding! 🚀
# Quickstart Guide

**Feature**: Smart Contract LLM Builder for Flow/Cadence
**Date**: 2025-09-25

## Prerequisites

### System Requirements
- Python 3.8+ installed
- Flow CLI installed and configured
- Git for version control
- Internet connection for API calls

### Account Setup
1. Obtain API keys for LLM providers (OpenAI, Groq)
2. Set up Flow blockchain account (testnet recommended for development)
3. Install and configure Flow CLI

### Environment Variables
```bash
# LLM Provider API Keys
OPENAI_API_KEY=your_openai_api_key
GROQ_API_KEY=your_groq_api_key

# Flow Configuration
FLOW_NETWORK=testnet
FLOW_ACCOUNT_ADDRESS=your_flow_address
FLOW_PRIVATE_KEY=your_private_key

# Database Configuration
DATABASE_URL=postgresql://user:pass@localhost/dbname
VECTOR_DB_URL=chroma:/path/to/vector/db

# Application Configuration
API_PORT=8000
LOG_LEVEL=INFO
MAX_FILE_SIZE=10485760  # 10MB
```

## Installation & Setup

### 1. Clone and Setup Repository
```bash
git clone <repository-url>
cd smart-contract-llm
git checkout 001-we-need-to

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Database Setup
```bash
# Run database migrations
python scripts/setup_db.py

# Initialize vector database
python scripts/init_vector_db.py

# Load Flow/Cadence documentation
python scripts/load_documentation.py
```

### 3. Flow CLI Configuration
```bash
# Verify Flow CLI installation
flow version

# Configure Flow project
flow project init --name=my-project
flow keys generate --key=google-kms # or your preferred key method
```

## Your First Contract Submission

### Option 1: Natural Language Input
```bash
# Submit natural language description
curl -X POST "http://localhost:8000/api/v1/contracts/submit" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your_api_key" \
  -d '{
    "input_type": "NATURAL_LANGUAGE",
    "content": "Create a simple NFT contract with minting capability",
    "pre_conditions": [
      {
        "condition": "minting_allowed",
        "parameters": {"amount": 1},
        "description": "Only allow minting of one NFT at a time"
      }
    ],
    "network": "testnet"
  }'
```

### Option 2: Existing Contract File
```bash
# Submit existing .cdc file
curl -X POST "http://localhost:8000/api/v1/contracts/submit" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your_api_key" \
  -d '{
    "input_type": "CDC_FILE",
    "content": "pub contract SimpleNFT { ... }",
    "network": "testnet"
  }'
```

### Monitor Processing
```bash
# Check submission status
curl -X GET "http://localhost:8000/api/v1/contracts/{submission_id}" \
  -H "Authorization: Bearer your_api_key"

# Expected response structure:
{
  "submission_id": "uuid",
  "status": "COMPLETED",
  "generated_contract": "pub contract SimpleNFT { ... }",
  "flow_config": {
    "contracts": { "SimpleNFT": { "source": "./SimpleNFT.cdc" } },
    "networks": { "testnet": "https://rest-testnet.onflow.org" }
  },
  "validation_errors": []
}
```

## Contract Deployment

### 1. Approve Transaction Proposal
```bash
# Get transaction proposals
curl -X GET "http://localhost:8000/api/v1/contracts/{submission_id}/proposals" \
  -H "Authorization: Bearer your_api_key"

# Approve deployment transaction
curl -X POST "http://localhost:8000/api/v1/proposals/{proposal_id}/approve" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your_api_key" \
  -d '{
    "signature": "your_transaction_signature",
    "signing_method": "LOCAL_KEY"
  }'
```

### 2. Monitor Deployment
```bash
# Check deployment status
curl -X GET "http://localhost:8000/api/v1/deployments/{deployment_id}" \
  -H "Authorization: Bearer your_api_key"

# Successful deployment response:
{
  "deployment_id": "string",
  "status": "COMPLETED",
  "network": "testnet",
  "transaction_hash": "0x123...",
  "gas_used": 42,
  "execution_time_ms": 1500,
  "log_content": "Deployment successful"
}
```

### 3. Verify on Blockchain
```bash
# Check contract on Flow blockchain
flow scripts execute ./scripts/check_contract.cdc \
  --network=testnet \
  --args="0xDeployedContractAddress"
```

## Web Interface Usage

### 1. Start Application
```bash
# Start the development server
python main.py

# Application will be available at:
# http://localhost:8000
# http://localhost:8000/docs (API documentation)
```

### 2. Web Interface Features
- **Dashboard**: Overview of submissions and deployments
- **Contract Builder**: Interactive contract creation interface
- **Deployment Monitor**: Real-time deployment status tracking
- **Documentation Search**: Search Flow/Cadence documentation
- **Analytics**: Learning insights and recommendations

### 3. WebSocket Connection
```javascript
// Connect to real-time updates
const ws = new WebSocket('ws://localhost:8000/ws/contracts/{submission_id}');

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Update:', data);
};

// Event types: PROCESSING_STARTED, DEPLOYMENT_STATUS, VALIDATION_COMPLETE
```

## Common Use Cases

### Use Case 1: Simple Token Contract
```bash
# Submit token contract request
curl -X POST "http://localhost:8000/api/v1/contracts/submit" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your_api_key" \
  -d '{
    "input_type": "NATURAL_LANGUAGE",
    "content": "Create a Fungible Token contract with initial supply of 1000 tokens",
    "network": "testnet"
  }'
```

### Use Case 2: NFT Marketplace
```bash
# Submit NFT marketplace request
curl -X POST "http://localhost:8000/api/v1/contracts/submit" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your_api_key" \
  -d '{
    "input_type": "NATURAL_LANGUAGE",
    "content": "Create an NFT marketplace with listing, buying, and selling functionality",
    "pre_conditions": [
      {
        "condition": "valid_listing",
        "parameters": {"min_price": 0.1},
        "description": "Minimum listing price of 0.1 FLOW"
      }
    ],
    "network": "testnet"
  }'
```

### Use Case 3: Contract Upgrade
```bash
# Submit existing contract for upgrade
curl -X POST "http://localhost:8000/api/v1/contracts/submit" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your_api_key" \
  -d '{
    "input_type": "CDC_FILE",
    "content": "pub contract ExistingContract { ... }",
    "post_conditions": [
      {
        "condition": "backward_compatible",
        "description": "Must maintain existing interface"
      }
    ],
    "network": "testnet"
  }'
```

## Testing Your Setup

### 1. Health Check
```bash
# Check API health
curl -X GET "http://localhost:8000/health"

# Check database connectivity
python scripts/test_db_connection.py

# Check Flow CLI integration
flow projects
```

### 2. Test Contract Generation
```bash
# Run test contract generation
python scripts/test_generation.py

# Expected output:
# ✓ Test contract generated successfully
# ✓ Validation passed
# ✓ Flow config created
```

### 3. Test Deployment Pipeline
```bash
# Run deployment test
python scripts/test_deployment.py

# Expected output:
# ✓ Contract deployed to testnet
# ✓ Transaction confirmed
# ✓ Logs captured successfully
```

## Troubleshooting

### Common Issues

#### 1. Authentication Failures
```bash
# Verify API key is valid
curl -X GET "http://localhost:8000/api/v1/users/me" \
  -H "Authorization: Bearer your_api_key"
```

#### 2. Flow CLI Issues
```bash
# Verify Flow CLI configuration
flow configuration show

# Test Flow connection
flow accounts list
```

#### 3. Database Connection Issues
```bash
# Check database status
python scripts/check_db_status.py

# Reset database if needed
python scripts/reset_db.py
```

#### 4. Vector Database Issues
```bash
# Reinitialize vector database
python scripts/reset_vector_db.py

# Reload documentation
python scripts/reload_docs.py
```

### Performance Issues

#### 1. Slow Response Times
- Check database query performance
- Verify vector database indexing
- Monitor memory usage
- Consider increasing cache size

#### 2. Deployment Failures
- Check network connectivity to Flow
- Verify gas limits and fees
- Review contract syntax
- Check Flow network status

### Getting Help

#### Documentation
- API Documentation: http://localhost:8000/docs
- Flow Documentation: https://docs.onflow.org
- Cadence Language Reference: https://docs.onflow.org/cadence/language/

#### Community
- GitHub Issues: https://github.com/your-repo/issues
- Discord Community: https://discord.gg/your-server
- Stack Overflow: [flow-blockchain] tag

#### Support
- Email Support: support@your-project.com
- Status Page: https://status.your-project.com
- Emergency Contact: emergency@your-project.com

## Next Steps

### 1. Explore Advanced Features
- Batch contract submissions
- Custom documentation integration
- Advanced learning patterns
- Multi-network deployments

### 2. Production Deployment
- Container orchestration with Docker/Kubernetes
- Load balancing and scaling
- Monitoring and alerting
- Backup and recovery procedures

### 3. Integration Examples
- CI/CD pipeline integration
- Web application integration
- Mobile app integration
- Third-party service integration

---

**Status**: Complete - Quickstart guide ready for testing
**Next**: Task generation and implementation planning
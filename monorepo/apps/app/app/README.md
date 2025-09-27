# Smart Contract LLM Builder

AI-powered smart contract generation and deployment platform for Flow blockchain using Cadence programming language.

## Features

- **Multi-modal Input Processing**: Accepts contracts via .cdc/.sol files or natural language descriptions
- **AI-Powered Generation**: Uses OpenAI/Groq LLMs to generate and optimize Cadence smart contracts
- **Flow Blockchain Integration**: Seamless deployment to Flow testnet/mainnet using Flow CLI
- **Real-time Learning**: Captures deployment logs to improve future contract generation
- **Documentation Intelligence**: Vector-powered documentation search for Cadence development
- **User Privacy Controls**: GDPR-compliant data management and export capabilities
- **Real-time Updates**: WebSocket-powered progress tracking and notifications
- **Web Interface**: Complete frontend for contract management and deployment

## Quick Start

### Prerequisites

- Python 3.8+
- Flow CLI installed and configured
- OpenAI API key or Groq API key
- PostgreSQL (recommended) or SQLite for development

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd smart-contract-llm
   ```

2. **Set up environment**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys and database settings
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Initialize database**
   ```bash
   alembic upgrade head
   ```

5. **Start the application**
   ```bash
   python src/main.py
   # Or use the start script
   ./start.sh
   ```

6. **Access the web interface**
   Open your browser and navigate to `http://localhost:8000`

## API Documentation

### Authentication

The API uses JWT tokens for authentication. Include the token in the Authorization header:

```
Authorization: Bearer <your-jwt-token>
```

### Endpoints

#### User Management

**Create User**
```http
POST /api/v1/users
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "secure_password",
  "persona_type": "DEVELOPER",
  "full_name": "John Doe"
}
```

**User Login**
```http
POST /api/v1/users/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "secure_password"
}
```

#### Contract Generation

**Generate Contract from Natural Language**
```http
POST /api/v1/contracts
Authorization: Bearer <token>
Content-Type: application/json

{
  "input_type": "NATURAL_LANGUAGE",
  "content": "Create a simple NFT contract with mint and transfer functions",
  "pre_conditions": {
    "accounts": {"user": "0x123"},
    "tokens": {"initial_supply": 1000}
  },
  "post_conditions": {
    "deployed_contracts": ["NFTContract"],
    "created_resources": ["NFT"]
  },
  "network": "testnet"
}
```

**Upload Contract File**
```http
POST /api/v1/contracts/file
Authorization: Bearer <token>
Content-Type: multipart/form-data

file: <contract-file>.cdc
```

#### Deployment

**Deploy Contract**
```http
POST /api/v1/contracts/{submission_id}/deploy
Authorization: Bearer <token>
Content-Type: application/json

{
  "network": "testnet",
  "config_id": "generated_config_id"
}
```

**Get Deployment Status**
```http
GET /api/v1/contracts/{submission_id}/deployments/{deployment_id}
Authorization: Bearer <token>
```

#### Documentation

**Search Documentation**
```http
POST /api/v1/documentation/search
Content-Type: application/json

{
  "query": "Cadence resources",
  "limit": 10,
  "use_semantic_search": true
}
```

**Get Documentation Statistics**
```http
GET /api/v1/documentation/stats
```

#### Learning & Analytics

**Get Learning Insights**
```http
GET /api/v1/learning/insights
Authorization: Bearer <token>
```

**Get System Statistics**
```http
GET /api/v1/statistics
Authorization: Bearer <token>
```

### WebSocket Connections

Connect to WebSocket for real-time updates:

```
ws://localhost:8000/ws
```

## Configuration

### Environment Variables

Create a `.env` file in the project root:

```env
# Application
APP_NAME=Smart Contract LLM Builder
DEBUG=false
HOST=0.0.0.0
PORT=8000

# Database
DATABASE_URL=postgresql://user:password@localhost/smart_contract_llm
# For development: sqlite:///./smart_contract_llm.db

# LLM Providers
OPENAI_API_KEY=your_openai_api_key
GROQ_API_KEY=your_groq_api_key
DEFAULT_LLM_PROVIDER=OPENAI

# Flow Blockchain
FLOW_NETWORK=testnet
FLOW_ACCOUNT_ADDRESS=your_flow_account_address
FLOW_PRIVATE_KEY=your_flow_private_key

# Security
JWT_SECRET_KEY=your_jwt_secret_key
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24

# CORS
ALLOWED_ORIGINS=["http://localhost:3000", "http://localhost:8000"]
```

### Database Configuration

For production deployment with PostgreSQL:

1. **Create database**
   ```sql
   CREATE DATABASE smart_contract_llm;
   CREATE USER smart_contract_user WITH PASSWORD 'your_password';
   GRANT ALL PRIVILEGES ON DATABASE smart_contract_llm TO smart_contract_user;
   ```

2. **Run migrations**
   ```bash
   alembic upgrade head
   ```

### Flow CLI Configuration

1. **Install Flow CLI**
   ```bash
   sh -ci "$(curl -fsSL https://storage.googleapis.com/flow-cli/install.sh)"
   ```

2. **Configure Flow project**
   ```bash
   flow project init
   flow keys generate
   ```

## Usage Examples

### This one works (internal notes)

```bash
python cli.py generate-from-context --stream --requirements "Create a simple NFT contract"
```

### Generate and Deploy a Simple NFT Contract

**Via API:**
```python
import requests
import json

# Login
login_response = requests.post('http://localhost:8000/api/v1/users/login', json={
    'email': 'user@example.com',
    'password': 'secure_password'
})
token = login_response.json()['access_token']

# Generate contract
headers = {'Authorization': f'Bearer {token}'}
contract_data = {
    'input_type': 'NATURAL_LANGUAGE',
    'content': 'Create a simple NFT contract with mint function that allows users to mint NFTs with unique IDs',
    'network': 'testnet'
}

response = requests.post(
    'http://localhost:8000/api/v1/contracts',
    json=contract_data,
    headers=headers
)

submission = response.json()
submission_id = submission['submission_id']

# Deploy contract
deploy_response = requests.post(
    f'http://localhost:8000/api/v1/contracts/{submission_id}/deploy',
    json={'network': 'testnet'},
    headers=headers
)

deployment = deploy_response.json()
print(f"Contract deployed with transaction hash: {deployment['transaction_hash']}")
```

**Via Web Interface:**
1. Open `http://localhost:8000` in your browser
2. Login or create a new account
3. Navigate to "Contract Generation"
4. Enter your contract requirements in natural language
5. Select the target network (testnet/mainnet)
6. Click "Generate Contract"
7. Review the generated contract and configuration
8. Click "Deploy" to deploy to Flow blockchain

### Upload and Deploy Existing Contract

**Via API:**
```python
import requests

# Upload contract file
with open('my_contract.cdc', 'rb') as f:
    files = {'file': f}
    response = requests.post(
        'http://localhost:8000/api/v1/contracts/file',
        files=files,
        headers={'Authorization': f'Bearer {token}'}
    )

submission = response.json()
submission_id = submission['submission_id']

# Deploy
deploy_response = requests.post(
    f'http://localhost:8000/api/v1/contracts/{submission_id}/deploy',
    json={'network': 'testnet'},
    headers=headers
)
```

### Search Documentation

**Via API:**
```python
import requests

# Search for documentation
search_data = {
    'query': 'How to create resources in Cadence',
    'limit': 5,
    'use_semantic_search': True
}

response = requests.post(
    'http://localhost:8000/api/v1/documentation/search',
    json=search_data
)

results = response.json()
for doc in results:
    print(f"{doc['title']}: {doc['content'][:100]}...")
```

## Testing

### Run Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src

# Run specific test file
pytest tests/test_api.py

# Run tests with markers
pytest -m "not llm"  # Skip LLM tests
pytest -m integration  # Run only integration tests
```

### Test Structure

- **Unit Tests**: Test individual components and functions
- **Integration Tests**: Test service interactions and database operations
- **API Tests**: Test REST endpoints and WebSocket connections
- **Performance Tests**: Test system performance under load

## Deployment

### Docker Deployment

1. **Build Docker image**
   ```bash
   docker build -t smart-contract-llm .
   ```

2. **Run with Docker Compose**
   ```bash
   docker-compose up -d
   ```

### Manual Deployment

1. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up database**
   ```bash
   alembic upgrade head
   ```

3. **Start application**
   ```bash
   gunicorn src.main:app -w 4 -k uvicorn.workers.UvicornWorker
   ```

### Environment Setup

**Production Environment:**
```env
DEBUG=false
DATABASE_URL=postgresql://user:password@prod-db/smart_contract_llm
ALLOWED_ORIGINS=["https://yourdomain.com"]
```

## Security Considerations

### API Security

- JWT-based authentication
- Rate limiting on all endpoints
- Input validation and sanitization
- CORS configuration for cross-origin requests
- Secure password hashing with bcrypt

### Data Privacy

- GDPR-compliant data handling
- User data export functionality
- Configurable data retention periods
- Anonymization of learning data
- Secure storage of sensitive information

### Blockchain Security

- Flow account key management
- Transaction validation
- Gas estimation and optimization
- Network-specific deployment configurations
- Audit logging for all blockchain operations

## Development

### Code Structure

```
src/
├── main.py                 # FastAPI application entry point
├── config.py              # Configuration management
├── models/                # Database models
│   ├── database.py        # Database connection and session management
│   ├── user.py            # User and data control models
│   ├── contract.py        # Contract and configuration models
│   └── learning.py        # Learning and documentation models
├── services/              # Business logic layer
│   ├── llm_service.py     # LLM provider integration
│   ├── flow_service.py    # Flow blockchain operations
│   ├── user_service.py    # User management
│   └── learning_service.py # Learning and documentation
├── api/                   # API layer
│   ├── routes.py          # REST API endpoints
│   ├── websocket.py       # WebSocket handlers
│   ├── auth.py            # Authentication middleware
│   └── middleware.py      # Request processing middleware
└── utils/                 # Utility functions
    ├── validators.py      # Input validation
    ├── security.py        # Security functions
    └── helpers.py         # Helper functions
```

### Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

### Development Setup

```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Set up pre-commit hooks
pre-commit install

# Run linting
flake8 src/
black src/
isort src/

# Run type checking
mypy src/
```

## Troubleshooting

### Common Issues

**Flow CLI not found:**
```bash
# Ensure Flow CLI is installed and in PATH
flow version

# Add to PATH if needed
export PATH=$PATH:/path/to/flow/cli
```

**Database connection issues:**
```bash
# Check database service status
sudo systemctl status postgresql

# Verify connection string
psql $DATABASE_URL -c "SELECT 1"
```

**LLM API errors:**
```bash
# Verify API keys are set
echo $OPENAI_API_KEY
echo $GROQ_API_KEY

# Test API connectivity
curl -H "Authorization: Bearer $OPENAI_API_KEY" https://api.openai.com/v1/models
```

### Performance Optimization

- Database indexing on frequently queried fields
- Connection pooling for database connections
- Caching for documentation search results
- Background job processing for long-running operations
- Efficient WebSocket connection management

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support, please:
1. Check the documentation
2. Search existing issues
3. Create a new issue with detailed information
4. Join our community discussions

## Roadmap

- [ ] Support for additional blockchain platforms
- [ ] Advanced contract optimization features
- [ ] Multi-signature contract deployment
- [ ] Contract verification and auditing tools
- [ ] Mobile application development
- [ ] Enhanced learning algorithms
- [ ] Enterprise features and compliance tools

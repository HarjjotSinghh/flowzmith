# User Guide

## Table of Contents

1. [Getting Started](#getting-started)
2. [User Registration and Login](#user-registration-and-login)
3. [Generating Smart Contracts](#generating-smart-contracts)
4. [Uploading Contract Files](#uploading-contract-files)
5. [Deploying Contracts](#deploying-contracts)
6. [Monitoring Deployments](#monitoring-deployments)
7. [Using Documentation Search](#using-documentation-search)
8. [Managing Your Account](#managing-your-account)
9. [Data Privacy and Export](#data-privacy-and-export)
10. [API Integration](#api-integration)
11. [Troubleshooting](#troubleshooting)

## Getting Started

### What is Smart Contract LLM Builder?

Smart Contract LLM Builder is an AI-powered platform that helps you create, test, and deploy smart contracts on the Flow blockchain. You can generate contracts using natural language descriptions or upload existing contract files for optimization and deployment.

### Key Features

- **Natural Language Contract Generation**: Describe your contract in plain English and let AI generate the Cadence code
- **File Upload Support**: Upload existing .cdc or .sol files for validation and deployment
- **Smart Contract Optimization**: AI-powered optimization suggestions for better performance and security
- **One-Click Deployment**: Deploy contracts directly to Flow testnet or mainnet
- **Real-time Learning**: The system learns from successful deployments to improve future suggestions
- **Documentation Search**: AI-powered search through Flow documentation and best practices
- **Privacy Controls**: Full control over your data with GDPR-compliant features

### Prerequisites

Before you start, ensure you have:

1. A Flow blockchain account (for deployment)
2. Basic understanding of smart contracts
3. For API usage: Python 3.8+ or Node.js 14+

## User Registration and Login

### Creating an Account

1. **Navigate to the Web Interface**
   - Open your browser and go to `http://localhost:8000`
   - Click "Sign Up" on the login page

2. **Fill in Registration Form**
   ```
   Email: your-email@example.com
   Password: YourSecurePassword123
   Confirm Password: YourSecurePassword123
   Full Name: John Doe
   Organization: Your Company (optional)
   Persona Type: Select the option that best describes you:
     - Developer: Technical user writing contracts
     - Business User: Non-technical user with contract requirements
     - Researcher: Academic or research-focused user
   ```

3. **Complete Registration**
   - Click "Create Account"
   - Check your email for verification (if enabled)
   - You'll be automatically logged in

### Logging In

1. **Navigate to Login Page**
   - Go to `http://localhost:8000`
   - Click "Login" if you're not already on the login page

2. **Enter Credentials**
   ```
   Email: your-email@example.com
   Password: YourSecurePassword123
   ```

3. **Access Your Dashboard**
   - After successful login, you'll be redirected to your dashboard
   - From here, you can access all features

### Profile Management

1. **Update Your Profile**
   - Click on your name in the top-right corner
   - Select "Profile Settings"
   - Update your information as needed

2. **Change Password**
   - Go to Profile Settings
   - Click "Change Password"
   - Enter current password, then new password
   - Click "Update Password"

## Generating Smart Contracts

### Understanding Natural Language Input

The AI can understand various types of descriptions:

- **Simple Contracts**: "Create a basic NFT contract with mint function"
- **Complex Contracts**: "Build a decentralized exchange with liquidity pools and fee mechanisms"
- **Specific Features**: "Add a pause function to my contract that only the owner can call"
- **Business Logic**: "Create a voting system where token holders can vote on proposals"

### Best Practices for Natural Language Descriptions

1. **Be Specific**
   ```
   Good: "Create an NFT contract with mint, transfer, and burn functions. Include admin controls and metadata support."
   Bad: "Make an NFT contract."
   ```

2. **Include Requirements**
   ```
   "Create a token contract with the following features:
   - Total supply of 1,000,000 tokens
   - Mint function controlled by admin
   - Transfer function with fee of 1%
   - Pause functionality for emergencies"
   ```

3. **Specify Constraints**
   ```
   "Create a staking contract where users can:
   - Stake tokens for minimum 30 days
   - Earn 5% APY rewards
   - Unstake anytime with 10% penalty if before 30 days"
   ```

### Step-by-Step Contract Generation

1. **Navigate to Contract Generation**
   - From your dashboard, click "Generate Contract"
   - Or use the sidebar navigation

2. **Choose Input Method**
   - Select "Natural Language" (default)
   - The other option is "File Upload"

3. **Enter Your Description**
   ```
   Example: "Create a simple NFT contract with the following features:
   - Each NFT has a unique ID and metadata
   - Only contract owner can mint new NFTs
   - Users can transfer their NFTs
   - Include a function to get NFT metadata by ID"
   ```

4. **Configure Pre-conditions (Optional)**
   - Click "Advanced Options"
   - Specify existing accounts or tokens:
   ```json
   {
     "accounts": {
       "admin": "0x123",
       "user": "0x456"
     },
     "tokens": {
       "payment_token": "A.123.Token"
     }
   }
   ```

5. **Set Post-conditions (Optional)**
   - Define what you expect the contract to create:
   ```json
   {
     "deployed_contracts": ["NFTContract"],
     "created_resources": ["NFT", "Collection"],
     "expected_functions": ["mint", "transfer", "getMetadata"]
   }
   ```

6. **Select Network**
   - Choose between "testnet" (recommended for testing) or "mainnet"

7. **Generate Contract**
   - Click "Generate Contract"
   - Wait for the AI to process your request
   - This typically takes 10-30 seconds

8. **Review Generated Code**
   - The system will display:
     - Generated Cadence code
     - Flow configuration (flow.json)
     - Validation results
     - Optimization suggestions

9. **Edit if Needed**
   - You can modify the generated code
   - Add custom logic or adjust existing code
   - The system will validate your changes

10. **Save or Proceed to Deployment**
    - Click "Save as Draft" to save for later
    - Or click "Deploy Contract" to proceed with deployment

### Example Contract Generation

**Input Description:**
```
"Create a fungible token contract with the following features:
- Total supply of 1,000,000 tokens
- Initial supply held by contract creator
- Transfer function that allows users to send tokens
- Balance function to check token balances
- Mint function that only the admin can call to create more tokens"
```

**Generated Code (Simplified):**
```cadence
pub contract FungibleToken {
    pub var totalSupply: UFix64
    pub let VaultStoragePath: StoragePath
    pub let VaultPublicPath: PublicPath

    pub resource Vault {
        pub var balance: UFix64

        init(balance: UFix64) {
            self.balance = balance
        }

        pub fun withdraw(amount: UFix64): @Vault {
            self.balance = self.balance - amount
            return <-create Vault(balance: amount)
        }

        pub fun deposit(from: @Vault) {
            self.balance = self.balance + from.balance
            destroy from
        }
    }

    pub resource Admin {
        pub fun mint(amount: UFix64) {
            FungibleToken.totalSupply = FungibleToken.totalSupply + amount
        }
    }

    init() {
        self.totalSupply = 1000000.0
        self.VaultStoragePath = /storage/fungibleTokenVault
        self.VaultPublicPath = /public/fungibleTokenVault

        let admin <- create Admin()
        self.account.save(<-admin, to: /storage/fungibleTokenAdmin)
    }
}
```

## Uploading Contract Files

### Supported File Types

- **.cdc files**: Cadence smart contracts (primary)
- **.sol files**: Solidity smart contracts (will be converted to Cadence)

### File Requirements

- Files must be valid smart contract code
- Maximum file size: 100KB
- Files should contain complete contract definitions
- Include necessary imports and resource definitions

### Step-by-Step File Upload

1. **Navigate to Contract Generation**
   - From dashboard, click "Generate Contract"

2. **Select File Upload**
   - Click on "File Upload" tab
   - Or click "Upload Contract File" button

3. **Choose File**
   - Click "Browse Files" or drag and drop
   - Select your .cdc or .sol file
   - The system will validate the file type

4. **Configure Upload Settings**
   - Select target network (testnet/mainnet)
   - Choose conversion options (for .sol files)
   - Add any additional requirements

5. **Upload and Process**
   - Click "Upload and Process"
   - The system will:
     - Validate the contract syntax
     - Analyze the contract structure
     - Generate Flow configuration
     - Provide optimization suggestions

6. **Review Results**
   - View validation results
   - Check generated configuration
   - Review optimization suggestions
   - Make any necessary edits

7. **Proceed or Save**
   - Save as draft or proceed to deployment

### Example File Upload Process

**Original File (simple_token.cdc):**
```cadence
pub contract SimpleToken {
    pub var totalSupply: UFix64

    pub resource Vault {
        pub var balance: UFix64

        init(balance: UFix64) {
            self.balance = balance
        }

        pub fun withdraw(amount: UFix64): @Vault {
            self.balance = self.balance - amount
            return <-create Vault(balance: amount)
        }

        pub fun deposit(from: @Vault) {
            self.balance = self.balance + from.balance
            destroy from
        }
    }

    init() {
        self.totalSupply = 1000.0
    }
}
```

**System Analysis Results:**
```
Validation: PASSED
Issues Found: 0
Optimizations Suggested:
- Add public capabilities for better accessibility
- Implement mint/burn functions
- Add event emissions for better tracking
- Include access controls for sensitive operations
```

## Deploying Contracts

### Prerequisites for Deployment

Before deploying, ensure you have:

1. **Flow Account**: A Flow blockchain account with sufficient funds
2. **Private Key**: Your account's private key (stored securely)
3. **Network Configuration**: Proper Flow CLI setup for your target network

### Understanding Deployment Networks

- **Testnet**: Development network for testing
  - Uses test tokens (no real value)
  - Faster transaction processing
  - Ideal for development and testing

- **Mainnet**: Production network for live contracts
  - Uses real FLOW tokens
  - Slower transaction processing
  - Permanent contract deployments

### Step-by-Step Deployment

1. **Access Deployment Screen**
   - After generating or uploading a contract, click "Deploy Contract"
   - Or select a saved contract from your dashboard and click "Deploy"

2. **Configure Deployment Settings**
   ```
   Network: testnet or mainnet
   Gas Limit: Auto or custom (recommended: Auto)
   Account: Select your Flow account
   Private Key: Enter your private key (encrypted storage)
   ```

3. **Review Contract Details**
   - Verify contract code
   - Check generated flow.json configuration
   - Review deployment parameters
   - Confirm gas estimates

4. **Execute Deployment**
   - Click "Deploy Contract"
   - The system will:
     - Compile the contract
     - Estimate gas costs
     - Submit transaction to Flow network
     - Monitor deployment progress

5. **Monitor Progress**
   - Real-time updates via WebSocket
   - View transaction hash
   - Track gas usage
   - Monitor contract status

6. **Deployment Complete**
   - Once deployed, you'll receive:
     - Contract address
     - Transaction hash
     - Gas used
     - Deployment timestamp
     - Contract interface

7. **Verify Deployment**
   - Use Flow CLI to verify:
   ```bash
   flow project deploy
   flow accounts get-contract <contract_name>
   ```

### Understanding Deployment Results

**Successful Deployment:**
```
Status: SUCCESS
Contract Address: 0x1654653399040a61
Transaction Hash: 4b8c7e3a1d9f2c5e6b8a0c1d2e3f4a5b6c7d8e9f0
Gas Used: 45
Execution Time: 2.3s
Contract Interface:
  - Functions: mint, transfer, balance
  - Resources: Vault
  - Events: TokensMinted, TokensTransferred
```

**Failed Deployment:**
```
Status: FAILED
Error: Insufficient gas limit
Error Details: Gas limit of 100 was too low. Required: 150.
Suggested Fix: Increase gas limit to 200 and retry.
```

### Post-Deployment Actions

1. **Test Your Contract**
   - Use Flow CLI to interact with deployed contract
   - Test all functions and edge cases
   - Verify expected behavior

2. **Monitor Contract Activity**
   - Use Flow Explorer to track transactions
   - Set up monitoring for contract events
   - Monitor gas usage patterns

3. **Document Your Contract**
   - Save deployment information
   - Document contract interface
   - Create usage examples

## Monitoring Deployments

### Accessing Deployment History

1. **From Dashboard**
   - Click "My Contracts" in sidebar
   - View all your contract submissions
   - Click on any contract to see deployment history

2. **Deployment Details Page**
   - Shows all deployment attempts
   - Status, timestamps, and transaction details
   - Gas usage and error information

### Understanding Deployment Status

- **PENDING**: Waiting to be processed
- **PROCESSING**: Currently being deployed
- **SUCCESS**: Successfully deployed
- **FAILED**: Deployment failed
- **TIMEOUT**: Deployment timed out
- **VALIDATION_ERROR**: Contract validation failed

### Real-time Monitoring

The system provides real-time updates for:

- Contract generation progress
- Deployment status changes
- Transaction confirmations
- Gas usage updates
- Error notifications

### Setting Up Notifications

1. **WebSocket Updates**
   - Connect via WebSocket for real-time updates
   - Receive instant notifications for status changes

2. **Email Notifications**
   - Enable email notifications in profile settings
   - Get notified about deployment completion or failures

3. **Webhook Integration**
   - Set up webhooks for programmatic notifications
   - Integrate with your existing systems

## Using Documentation Search

### Accessing Documentation Search

1. **From Navigation**
   - Click "Documentation" in sidebar
   - Or use the search bar in the header

2. **Search Interface**
   - Enter your query in natural language
   - Use filters for specific content types
   - Choose search scope

### Effective Search Queries

- **Technical Questions**: "How to create resources in Cadence?"
- **Best Practices**: "What are the security considerations for NFT contracts?"
- **Specific Features**: "How to implement access controls in Flow contracts?"
- **Error Solutions**: "What does 'insufficient gas' mean in Flow?"

### Search Results

Results include:

- **Relevance Score**: How well the result matches your query
- **Content Type**: Tutorial, API reference, language spec, etc.
- **Source**: Official docs, community content, custom docs
- **Preview**: Snippet of the relevant content
- **Metadata**: Version, last updated, etc.

### Search Filters

- **Content Type**: Filter by tutorial, reference, examples
- **Source**: Filter by official docs, community, custom
- **Date Range**: Filter by document age
- **Semantic Search**: Enable/disable AI-powered search

### Saving Search Results

- Bookmark important results for future reference
- Export search results for offline use
- Share results with team members

## Managing Your Account

### Profile Management

1. **Update Personal Information**
   - Name, email, organization
   - Persona type and preferences

2. **Security Settings**
   - Change password
   - Enable two-factor authentication
   - Review active sessions

3. **Notification Preferences**
   - Email notifications
   - In-app notifications
   - Webhook configurations

### Data Control Settings

1. **Privacy Settings**
   - Data retention period
   - Learning data usage
   - Analytics sharing
   - Marketing consent

2. **Data Export**
   - Export all your data
   - Choose export format (JSON, CSV)
   - Include specific data types

3. **Account Management**
   - Deactivate account
   - Request data deletion
   - Export data before deletion

### Understanding Data Retention

- **One Month**: Data deleted after 30 days
- **Six Months**: Data deleted after 6 months
- **One Year**: Data deleted after 1 year
- **Indefinite**: Data kept until manually deleted

### Subscription and Billing

- **Free Tier**: Limited contract generations and deployments
- **Pro Tier**: Unlimited generations, priority processing
- **Enterprise**: Custom features, dedicated support

## Data Privacy and Export

### Understanding Your Data Rights

- **Right to Access**: View all data stored about you
- **Right to Export**: Download your data in standard formats
- **Right to Delete**: Request deletion of your data
- **Right to Opt-out**: Control how your data is used

### Data Types Collected

1. **Profile Data**
   - Name, email, organization
   - Persona type and preferences

2. **Contract Data**
   - Generated contracts and configurations
   - Deployment history and logs
   - Natural language inputs

3. **Usage Data**
   - Feature usage patterns
   - Learning and improvement data
   - Performance metrics

### Exporting Your Data

1. **Request Export**
   - Go to Account Settings
   - Click "Export Data"
   - Choose data types to include
   - Select export format

2. **Download Export**
   - Receive email when export is ready
   - Download from secure link
   - Link expires after 7 days

3. **Export Formats**
   - **JSON**: Machine-readable, ideal for API use
   - **CSV**: Spreadsheet-compatible, easy to analyze
   - **PDF**: Human-readable, includes formatting

### Data Deletion

1. **Request Deletion**
   - Go to Account Settings
   - Click "Delete Account"
   - Confirm deletion request

2. **Deletion Process**
   - Immediate anonymization of personal data
   - Contract data kept for audit purposes (if required)
   - Full deletion after retention period

### Learning Data Usage

The system uses deployment data to improve:

- Contract generation accuracy
- Deployment success rates
- Error detection and prevention
- Optimization suggestions

You can opt-out of learning data usage while keeping full functionality.

## API Integration

### Getting API Access

1. **Generate API Key**
   - Go to Account Settings
   - Click "API Keys"
   - Generate new API key
   - Copy key securely

2. **Authentication**
   - Use JWT tokens for authentication
   - Include token in Authorization header
   - Refresh tokens before expiration

### API Endpoints

Key endpoints for integration:

- `POST /users/login` - Authenticate and get token
- `POST /contracts` - Generate contract from description
- `POST /contracts/file` - Upload contract file
- `POST /contracts/{id}/deploy` - Deploy contract
- `GET /contracts` - List user contracts
- `POST /documentation/search` - Search documentation

### Python SDK Example

```python
import requests
import json

class SmartContractClient:
    def __init__(self, base_url="http://localhost:8000/api/v1"):
        self.base_url = base_url
        self.token = None

    def login(self, email, password):
        response = requests.post(f"{self.base_url}/users/login",
                                json={'email': email, 'password': password})
        data = response.json()
        self.token = data['data']['access_token']
        return data

    def generate_contract(self, description, network="testnet"):
        headers = {'Authorization': f'Bearer {self.token}'}
        response = requests.post(f"{self.base_url}/contracts",
                               json={'input_type': 'NATURAL_LANGUAGE',
                                    'content': description,
                                    'network': network},
                               headers=headers)
        return response.json()

    def deploy_contract(self, submission_id, network="testnet"):
        headers = {'Authorization': f'Bearer {self.token}'}
        response = requests.post(f"{self.base_url}/contracts/{submission_id}/deploy",
                               json={'network': network},
                               headers=headers)
        return response.json()

# Usage
client = SmartContractClient()
client.login('user@example.com', 'password')
result = client.generate_contract('Create a simple NFT contract')
submission_id = result['data']['submission_id']
deployment = client.deploy_contract(submission_id)
```

### JavaScript SDK Example

```javascript
class SmartContractClient {
    constructor(baseUrl = 'http://localhost:8000/api/v1') {
        this.baseUrl = baseUrl;
        this.token = null;
    }

    async login(email, password) {
        const response = await fetch(`${this.baseUrl}/users/login`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({email, password})
        });
        const data = await response.json();
        this.token = data.data.access_token;
        return data;
    }

    async generateContract(description, network = 'testnet') {
        const response = await fetch(`${this.baseUrl}/contracts`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${this.token}`
            },
            body: JSON.stringify({
                input_type: 'NATURAL_LANGUAGE',
                content: description,
                network
            })
        });
        return response.json();
    }

    async deployContract(submissionId, network = 'testnet') {
        const response = await fetch(`${this.baseUrl}/contracts/${submissionId}/deploy`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${this.token}`
            },
            body: JSON.stringify({network})
        });
        return response.json();
    }
}

// Usage
const client = new SmartContractClient();
await client.login('user@example.com', 'password');
const result = await client.generateContract('Create a simple NFT contract');
const submissionId = result.data.submission_id;
const deployment = await client.deployContract(submissionId);
```

### WebSocket Integration

```javascript
// Connect to WebSocket for real-time updates
const ws = new WebSocket('ws://localhost:8000/api/v1/ws/updates?token=YOUR_JWT_TOKEN');

ws.onmessage = function(event) {
    const data = JSON.parse(event.data);
    console.log('Received update:', data);

    if (data.type === 'update' && data.event === 'deployment_completed') {
        console.log('Deployment completed:', data.data);
    }
};

// Subscribe to updates
ws.send(JSON.stringify({
    type: 'subscribe',
    channels: ['deployment_status', 'contract_updates']
}));
```

## Troubleshooting

### Common Issues and Solutions

#### 1. Login Problems

**Issue**: Invalid credentials error
**Solution**:
- Verify email and password
- Check if account is activated
- Reset password if needed

**Issue**: JWT token expired
**Solution**:
- Log in again to get new token
- Implement token refresh in your code

#### 2. Contract Generation Issues

**Issue**: Generation taking too long
**Solution**:
- Wait up to 60 seconds for complex contracts
- Break down complex requirements into simpler parts
- Check system status page for outages

**Issue**: Poor quality generated code
**Solution**:
- Be more specific in your description
- Include examples or requirements
- Try rephrasing your request

#### 3. Deployment Issues

**Issue**: Deployment failed with gas error
**Solution**:
- Increase gas limit for deployment
- Optimize contract code
- Check current network gas prices

**Issue**: "Account not found" error
**Solution**:
- Verify Flow account address
- Ensure account exists on target network
- Check account balance for gas fees

#### 4. File Upload Issues

**Issue**: File type not supported
**Solution**:
- Use .cdc or .sol files only
- Ensure file extension is correct
- Check file size (max 100KB)

**Issue**: Validation failed
**Solution**:
- Check contract syntax
- Ensure all imports are valid
- Verify resource definitions

#### 5. Network Issues

**Issue**: Cannot connect to API
**Solution**:
- Check internet connection
- Verify API endpoint URL
- Check for service outages

**Issue**: Slow response times
**Solution**:
- Check network connectivity
- Try during off-peak hours
- Use smaller contract files

### Getting Help

1. **Documentation**
   - Read this user guide
   - Check API documentation
   - Review code examples

2. **Support Channels**
   - Email support
   - Community forum
   - Discord/Slack channels

3. **Debug Information**
   - Check browser console for errors
   - Review API response messages
   - Check system logs for server issues

### Best Practices

1. **Contract Development**
   - Start with simple contracts
   - Test thoroughly on testnet
   - Review generated code before deployment

2. **Security**
   - Keep API keys secure
   - Use strong passwords
   - Enable two-factor authentication

3. **Performance**
   - Use appropriate gas limits
   - Optimize contract code
   - Monitor deployment times

### Contact Support

For additional help:
- Email: support@smartcontractllm.com
- Documentation: docs.smartcontractllm.com
- Status: status.smartcontractllm.com
- Community: community.smartcontractllm.com
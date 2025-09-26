# API Contracts

**Feature**: Smart Contract LLM Builder for Flow/Cadence
**Date**: 2025-09-25

## REST API Endpoints

### Contract Submission Endpoints

#### POST /api/v1/contracts/submit
Submit a contract for processing and deployment.

**Request Body**:
```json
{
  "input_type": "CDC_FILE | SOL_FILE | NATURAL_LANGUAGE | MIXED",
  "content": "string",
  "pre_conditions": {},
  "post_conditions": {},
  "network": "testnet | mainnet | emulator"
}
```

**Response**:
```json
{
  "submission_id": "uuid",
  "status": "PENDING | PROCESSING | COMPLETED | FAILED",
  "estimated_processing_time": "integer",
  "created_at": "timestamp"
}
```

**Status Codes**:
- 201: Created - Submission accepted
- 400: Bad Request - Invalid input format
- 401: Unauthorized - Authentication required
- 422: Unprocessable Entity - Validation failed

#### GET /api/v1/contracts/{submission_id}
Retrieve contract submission status and results.

**Response**:
```json
{
  "submission_id": "uuid",
  "status": "enum",
  "input_type": "enum",
  "generated_contract": "string",
  "flow_config": "object",
  "deployment_logs": [],
  "validation_errors": [],
  "created_at": "timestamp",
  "processed_at": "timestamp"
}
```

**Status Codes**:
- 200: OK - Submission retrieved
- 404: Not Found - Submission not found
- 401: Unauthorized - Authentication required

### Deployment Management

#### POST /api/v1/contracts/{submission_id}/deploy
Initiate contract deployment to Flow blockchain.

**Request Body**:
```json
{
  "network": "testnet | mainnet | emulator",
  "gas_limit": "integer (optional)",
  "timeout_seconds": "integer (optional)"
}
```

**Response**:
```json
{
  "deployment_id": "string",
  "submission_id": "uuid",
  "status": "INITIATED | IN_PROGRESS | COMPLETED | FAILED",
  "estimated_gas": "integer",
  "transaction_hash": "string (optional)",
  "created_at": "timestamp"
}
```

#### GET /api/v1/deployments/{deployment_id}
Retrieve deployment status and logs.

**Response**:
```json
{
  "deployment_id": "string",
  "submission_id": "uuid",
  "status": "enum",
  "network": "string",
  "transaction_hash": "string (optional)",
  "gas_used": "integer (optional)",
  "execution_time_ms": "integer",
  "error_message": "string (optional)",
  "error_code": "string (optional)",
  "log_content": "string",
  "created_at": "timestamp"
}
```

### Transaction Management

#### GET /api/v1/contracts/{submission_id}/proposals
Get transaction proposals for user approval.

**Response**:
```json
{
  "proposals": [
    {
      "proposal_id": "uuid",
      "transaction_type": "DEPLOY | UPDATE | INTERACT",
      "transaction_data": "object",
      "estimated_gas": "integer",
      "created_at": "timestamp"
    }
  ]
}
```

#### POST /api/v1/proposals/{proposal_id}/approve
Approve and sign a transaction proposal.

**Request Body**:
```json
{
  "signature": "string",
  "signing_method": "LOCAL_KEY | WALLET_CONNECT | HARDWARE_WALLET"
}
```

**Response**:
```json
{
  "proposal_id": "uuid",
  "status": "APPROVED | REJECTED | EXECUTED",
  "signed_transaction": "string (optional)",
  "transaction_hash": "string (optional)",
  "responded_at": "timestamp"
}
```

### User Management

#### POST /api/v1/users/register
Register a new user account.

**Request Body**:
```json
{
  "email": "string",
  "persona_type": "EXPERT | INTERMEDIATE | BEGINNER | NON_TECHNICAL",
  "flow_account_address": "string (optional)",
  "preferences": {}
}
```

**Response**:
```json
{
  "user_id": "uuid",
  "email": "string",
  "persona_type": "enum",
  "api_key": "string",
  "created_at": "timestamp"
}
```

#### GET /api/v1/users/{user_id}/data-control
Get user data control preferences.

**Response**:
```json
{
  "user_id": "uuid",
  "data_retention_preference": "enum",
  "learning_consent": "boolean",
  "deletion_requests": [],
  "last_data_access": "timestamp (optional)",
  "created_at": "timestamp",
  "updated_at": "timestamp"
}
```

#### PUT /api/v1/users/{user_id}/data-control
Update user data control preferences.

**Request Body**:
```json
{
  "data_retention_preference": "enum",
  "learning_consent": "boolean",
  "request_deletion": "boolean"
}
```

### Documentation Search

#### GET /api/v1/documentation/search
Search through Flow and Cadence documentation.

**Query Parameters**:
- `q` (string): Search query
- `type` (string): Filter by content type
- `limit` (integer): Results limit (default: 10)
- `offset` (integer): Results offset (default: 0)

**Response**:
```json
{
  "results": [
    {
      "doc_id": "uuid",
      "title": "string",
      "content_type": "enum",
      "snippet": "string",
      "relevance_score": "float",
      "source_url": "string"
    }
  ],
  "total_results": "integer",
  "query": "string"
}
```

### Analytics & Feedback

#### GET /api/v1/analytics/user/{user_id}/insights
Get learning insights and recommendations for a user.

**Response**:
```json
{
  "user_id": "uuid",
  "insights": [
    {
      "insight_id": "uuid",
      "pattern_type": "enum",
      "description": "string",
      "confidence_score": "float",
      "recommendation": "string"
    }
  ],
  "success_rate": "float",
  "common_errors": [],
  "generated_at": "timestamp"
}
```

## WebSocket Events

### Real-time Updates

#### Connection: ws://api.example.com/ws/contracts/{submission_id}
Subscribe to real-time updates for contract processing.

**Event Types**:
```json
{
  "event": "PROCESSING_STARTED",
  "submission_id": "uuid",
  "timestamp": "timestamp",
  "message": "string"
}

{
  "event": "DEPLOYMENT_STATUS",
  "deployment_id": "string",
  "status": "enum",
  "progress": "integer (0-100)",
  "timestamp": "timestamp"
}

{
  "event": "VALIDATION_COMPLETE",
  "submission_id": "uuid",
  "validation_status": "enum",
  "errors": [],
  "timestamp": "timestamp"
}
```

## Error Handling

### Standard Error Response
```json
{
  "error": {
    "code": "string",
    "message": "string",
    "details": {},
    "request_id": "string"
  }
}
```

### Common Error Codes
- `AUTH_REQUIRED`: Authentication required
- `INVALID_INPUT`: Invalid request format
- `RESOURCE_NOT_FOUND`: Requested resource not found
- `VALIDATION_FAILED`: Input validation failed
- `DEPLOYMENT_FAILED`: Contract deployment failed
- `NETWORK_ERROR`: Network connectivity issue
- `RATE_LIMITED`: Too many requests

## Data Formats

### Flow Configuration Schema
```json
{
  "contracts": {
    "ContractName": {
      "source": "./path/to/contract.cdc",
      "aliases": {
        "network": "0xContractAddress"
      }
    }
  },
  "networks": {
    "emulator": "http://localhost:8080",
    "testnet": "https://rest-testnet.onflow.org",
    "mainnet": "https://rest-mainnet.onflow.org"
  },
  "accounts": {
    "emulator-account": {
      "address": "0xf8d6e0586b0a20c7",
      "key": "private-key"
    }
  },
  "deployments": {
    "testnet": {
      "testnet-account": [
        "ContractName"
      ]
    }
  }
}
```

### Pre/Post Conditions Format
```json
{
  "pre_conditions": [
    {
      "condition": "string",
      "parameters": {},
      "description": "string"
    }
  ],
  "post_conditions": [
    {
      "condition": "string",
      "parameters": {},
      "description": "string"
    }
  ]
}
```

### Deployment Log Structure
```json
{
  "deployment_id": "string",
  "timestamp": "timestamp",
  "level": "INFO | WARN | ERROR",
  "message": "string",
  "code": "string",
  "details": {},
  "network": "string",
  "contract_name": "string"
}
```

## Authentication

### API Key Authentication
```
Authorization: Bearer <api_key>
```

### User Authentication
```
Authorization: Bearer <jwt_token>
```

---

**Status**: Complete - All major API contracts defined
**Next**: Quickstart documentation and testing strategy
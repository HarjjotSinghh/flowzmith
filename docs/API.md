# API Documentation

## Overview

The Smart Contract LLM Builder API provides RESTful endpoints for smart contract generation, deployment, and management on the Flow blockchain. The API uses JWT authentication and provides real-time updates via WebSocket connections.

## Base URL

```
http://localhost:8000/api/v1
```

## Authentication

All protected endpoints require JWT authentication. Include the token in the Authorization header:

```
Authorization: Bearer <your-jwt-token>
```

### JWT Token Format

The JWT token contains the following claims:
- `sub`: User ID
- `email`: User email
- `persona_type`: User persona type
- `exp`: Expiration timestamp
- `iat`: Issued at timestamp

## Response Format

All API responses follow this standard format:

### Success Response
```json
{
  "success": true,
  "data": {},
  "message": "Operation completed successfully",
  "timestamp": "2025-01-01T00:00:00Z"
}
```

### Error Response
```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "Error description",
    "details": {}
  },
  "timestamp": "2025-01-01T00:00:00Z"
}
```

## Error Codes

| Code | HTTP Status | Description |
|------|-------------|-------------|
| `VALIDATION_ERROR` | 422 | Request validation failed |
| `AUTHENTICATION_ERROR` | 401 | Authentication required |
| `AUTHORIZATION_ERROR` | 403 | Insufficient permissions |
| `NOT_FOUND` | 404 | Resource not found |
| `CONFLICT` | 409 | Resource conflict |
| `INTERNAL_ERROR` | 500 | Internal server error |
| `RATE_LIMIT_EXCEEDED` | 429 | Rate limit exceeded |

## Endpoints

### Health Check

#### GET /health
Check API health status.

**Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "timestamp": "2025-01-01T00:00:00Z",
  "database": "connected",
  "llm_providers": {
    "openai": "available",
    "groq": "available"
  },
  "flow_cli": "available"
}
```

### User Management

#### POST /users
Create a new user account.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "secure_password123",
  "persona_type": "DEVELOPER",
  "full_name": "John Doe",
  "organization": "Company Name"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "user_id",
    "email": "user@example.com",
    "persona_type": "DEVELOPER",
    "full_name": "John Doe",
    "organization": "Company Name",
    "is_active": true,
    "created_at": "2025-01-01T00:00:00Z"
  },
  "message": "User created successfully"
}
```

#### POST /users/login
Authenticate user and return JWT token.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "secure_password123"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "access_token": "jwt_token",
    "token_type": "bearer",
    "expires_in": 86400,
    "user": {
      "id": "user_id",
      "email": "user@example.com",
      "persona_type": "DEVELOPER"
    }
  },
  "message": "Login successful"
}
```

#### GET /users/me
Get current user profile.

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "user_id",
    "email": "user@example.com",
    "persona_type": "DEVELOPER",
    "full_name": "John Doe",
    "organization": "Company Name",
    "is_active": true,
    "created_at": "2025-01-01T00:00:00Z",
    "last_login": "2025-01-01T12:00:00Z"
  }
}
```

#### PUT /users/me
Update user profile.

**Request Body:**
```json
{
  "full_name": "Updated Name",
  "organization": "Updated Company",
  "persona_type": "BUSINESS_USER"
}
```

#### DELETE /users/me
Deactivate user account.

**Response:**
```json
{
  "success": true,
  "message": "User deactivated successfully"
}
```

### Contract Generation

#### POST /contracts
Generate a smart contract from natural language description.

**Request Body:**
```json
{
  "input_type": "NATURAL_LANGUAGE",
  "content": "Create a simple NFT contract with mint and transfer functions",
  "pre_conditions": {
    "accounts": {
      "user": "0x123",
      "admin": "0x456"
    },
    "tokens": {
      "initial_supply": 1000,
      "token_name": "MyToken"
    }
  },
  "post_conditions": {
    "deployed_contracts": ["NFTContract"],
    "created_resources": ["NFT", "Collection"],
    "expected_functions": ["mint", "transfer", "balance"]
  },
  "network": "testnet"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "submission_id": "submission_id",
    "user_id": "user_id",
    "input_type": "NATURAL_LANGUAGE",
    "content": "Create a simple NFT contract...",
    "status": "PROCESSING",
    "generated_config": {
      "id": "config_id",
      "config_content": {
        "contracts": {
          "NFTContract": {
            "source": "./NFTContract.cdc",
            "aliases": {
              "testnet": "0x123"
            }
          }
        },
        "networks": {
          "testnet": {
            "host": "access.devnet.nodes.onflow.org:9000",
            "chain": "flow-emulator"
          }
        },
        "accounts": {
          "testnet-account": {
            "address": "0x123",
            "key": "private-key"
          }
        }
      },
      "generated_contract_code": "pub contract NFTContract {...}",
      "validation_status": "VALID",
      "llm_metadata": {
        "provider": "OPENAI",
        "model": "gpt-4",
        "tokens_used": 500,
        "cost": 0.01,
        "generation_time_ms": 2000
      }
    },
    "created_at": "2025-01-01T00:00:00Z"
  }
}
```

#### POST /contracts/file
Upload a contract file for processing.

**Request:**
```
Content-Type: multipart/form-data

file: <contract-file>.cdc
network: testnet (optional)
```

**Response:**
```json
{
  "success": true,
  "data": {
    "submission_id": "submission_id",
    "user_id": "user_id",
    "input_type": "CDC_FILE",
    "content": "Uploaded contract file content",
    "status": "PROCESSING",
    "generated_config": {
      "id": "config_id",
      "config_content": {...},
      "generated_contract_code": "pub contract UploadedContract {...}",
      "validation_status": "PENDING"
    }
  }
}
```

#### GET /contracts/{submission_id}
Get contract submission details.

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "submission_id",
    "user_id": "user_id",
    "input_type": "NATURAL_LANGUAGE",
    "content": "Create a simple NFT contract...",
    "status": "COMPLETED",
    "pre_conditions": {...},
    "post_conditions": {...},
    "generated_config": {...},
    "deployments": [...],
    "created_at": "2025-01-01T00:00:00Z",
    "updated_at": "2025-01-01T00:05:00Z"
  }
}
```

#### GET /contracts
List user's contract submissions.

**Query Parameters:**
- `limit`: Maximum number of results (default: 10, max: 100)
- `offset`: Number of results to skip (default: 0)
- `status`: Filter by status (PENDING, PROCESSING, COMPLETED, FAILED)
- `input_type`: Filter by input type (NATURAL_LANGUAGE, CDC_FILE, SOL_FILE)

**Response:**
```json
{
  "success": true,
  "data": {
    "submissions": [...],
    "total": 25,
    "limit": 10,
    "offset": 0
  }
}
```

### Contract Deployment

#### POST /contracts/{submission_id}/deploy
Deploy a contract to the blockchain.

**Request Body:**
```json
{
  "network": "testnet",
  "config_id": "config_id",
  "gas_limit": 1000
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "deployment_id": "deployment_id",
    "submission_id": "submission_id",
    "config_id": "config_id",
    "network": "testnet",
    "status": "SUCCESS",
    "transaction_hash": "0xabcdef123456789",
    "contract_address": "0x987654321",
    "gas_used": 150,
    "execution_time_ms": 2500,
    "log_content": "Deployment completed successfully",
    "created_at": "2025-01-01T00:10:00Z"
  }
}
```

#### GET /contracts/{submission_id}/deployments
Get deployment history for a submission.

**Response:**
```json
{
  "success": true,
  "data": {
    "deployments": [
      {
        "id": "deployment_id",
        "network": "testnet",
        "status": "SUCCESS",
        "transaction_hash": "0xabcdef123456789",
        "gas_used": 150,
        "execution_time_ms": 2500,
        "created_at": "2025-01-01T00:10:00Z"
      }
    ]
  }
}
```

#### GET /contracts/{submission_id}/deployments/{deployment_id}
Get specific deployment details.

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "deployment_id",
    "submission_id": "submission_id",
    "config_id": "config_id",
    "network": "testnet",
    "status": "SUCCESS",
    "transaction_hash": "0xabcdef123456789",
    "contract_address": "0x987654321",
    "gas_used": 150,
    "execution_time_ms": 2500,
    "log_content": "Deployment completed successfully. Transaction ID: 0xabcdef123456789",
    "error_details": null,
    "created_at": "2025-01-01T00:10:00Z"
  }
}
```

### Documentation

#### POST /documentation/search
Search documentation.

**Request Body:**
```json
{
  "query": "How to create resources in Cadence",
  "limit": 10,
  "use_semantic_search": true,
  "content_types": ["LANGUAGE_SPEC", "TUTORIAL"],
  "sources": ["OFFICIAL_FLOW_DOCS"]
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "results": [
      {
        "id": "doc_id",
        "title": "Cadence Resources",
        "content": "Resources in Cadence are unique types...",
        "content_type": "LANGUAGE_SPEC",
        "source": "OFFICIAL_FLOW_DOCS",
        "relevance_score": 0.95,
        "version": "1.0.0",
        "last_updated": "2025-01-01T00:00:00Z"
      }
    ],
    "total_results": 15,
    "search_time_ms": 50
  }
}
```

#### GET /documentation/stats
Get documentation statistics.

**Response:**
```json
{
  "success": true,
  "data": {
    "total_documents": 1250,
    "documents_by_type": {
      "LANGUAGE_SPEC": 150,
      "API_REFERENCE": 300,
      "TUTORIAL": 200,
      "EXAMPLE": 600
    },
    "documents_by_source": {
      "OFFICIAL_FLOW_DOCS": 800,
      "COMMUNITY": 300,
      "CUSTOM": 150
    },
    "last_indexed": "2025-01-01T00:00:00Z"
  }
}
```

### Learning & Analytics

#### GET /learning/insights
Get learning insights and patterns.

**Query Parameters:**
- `limit`: Maximum number of insights (default: 10)
- `pattern_type`: Filter by pattern type (SUCCESS_PATTERN, ERROR_PATTERN, OPTIMIZATION_OPPORTUNITY)

**Response:**
```json
{
  "success": true,
  "data": {
    "insights": [
      {
        "id": "insight_id",
        "pattern_type": "SUCCESS_PATTERN",
        "insights": {
          "pattern_type": "deployment_success",
          "elements": [
            {"practice": "proper_resource_definition", "found": true},
            {"practice": "error_handling", "found": true}
          ]
        },
        "confidence_score": 0.85,
        "applied_to_generation": true,
        "created_at": "2025-01-01T00:00:00Z"
      }
    ]
  }
}
```

#### GET /learning/stats
Get learning statistics.

**Response:**
```json
{
  "success": true,
  "data": {
    "total_patterns": 250,
    "patterns_by_type": {
      "SUCCESS_PATTERN": 150,
      "ERROR_PATTERN": 75,
      "OPTIMIZATION_OPPORTUNITY": 25
    },
    "average_confidence_score": 0.78,
    "patterns_applied_to_generation": 180,
    "learning_accuracy": 0.85
  }
}
```

### System Statistics

#### GET /statistics
Get system statistics.

**Response:**
```json
{
  "success": true,
  "data": {
    "users": {
      "total": 150,
      "active": 120,
      "by_persona_type": {
        "DEVELOPER": 100,
        "BUSINESS_USER": 30,
        "RESEARCHER": 20
      }
    },
    "contracts": {
      "total_submissions": 500,
      "successful_deployments": 350,
      "success_rate": 0.7,
      "by_input_type": {
        "NATURAL_LANGUAGE": 300,
        "CDC_FILE": 150,
        "SOL_FILE": 50
      }
    },
    "deployments": {
      "total": 400,
      "successful": 350,
      "failed": 50,
      "average_gas_used": 200,
      "average_execution_time_ms": 3000
    },
    "system": {
      "uptime": "15 days",
      "version": "1.0.0",
      "last_deployed": "2025-01-01T00:00:00Z"
    }
  }
}
```

### Data Control

#### GET /users/me/data-control
Get user data control settings.

**Response:**
```json
{
  "success": true,
  "data": {
    "user_id": "user_id",
    "data_retention_period": "ONE_YEAR",
    "allow_learning_data_usage": true,
    "allow_analytics_sharing": false,
    "marketing_consent": false,
    "export_format_preference": "JSON",
    "last_updated": "2025-01-01T00:00:00Z"
  }
}
```

#### PUT /users/me/data-control
Update user data control settings.

**Request Body:**
```json
{
  "data_retention_period": "SIX_MONTHS",
  "allow_learning_data_usage": false,
  "allow_analytics_sharing": false,
  "marketing_consent": false,
  "export_format_preference": "CSV"
}
```

#### POST /users/me/export-data
Export user data.

**Request Body:**
```json
{
  "format": "JSON",
  "include": ["profile", "contracts", "deployments", "learning_data"]
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "export_id": "export_id",
    "format": "JSON",
    "status": "PROCESSING",
    "download_url": null,
    "expires_at": "2025-01-02T00:00:00Z"
  }
}
```

#### GET /users/me/export-data/{export_id}
Get export status and download URL.

**Response:**
```json
{
  "success": true,
  "data": {
    "export_id": "export_id",
    "format": "JSON",
    "status": "COMPLETED",
    "download_url": "https://example.com/exports/export_id.json",
    "expires_at": "2025-01-02T00:00:00Z",
    "created_at": "2025-01-01T00:00:00Z"
  }
}
```

## WebSocket API

### Connection

Connect to WebSocket for real-time updates:

```
ws://localhost:8000/api/v1/ws/updates?token=<jwt-token>
```

### Message Format

#### Server to Client Messages

**Update Message:**
```json
{
  "type": "update",
  "event": "contract_generated",
  "data": {
    "submission_id": "submission_id",
    "status": "COMPLETED",
    "generated_config": {...}
  },
  "timestamp": "2025-01-01T00:00:00Z"
}
```

**Error Message:**
```json
{
  "type": "error",
  "code": "DEPLOYMENT_FAILED",
  "message": "Contract deployment failed",
  "details": {
    "submission_id": "submission_id",
    "error": "Insufficient gas"
  },
  "timestamp": "2025-01-01T00:00:00Z"
}
```

#### Client to Server Messages

**Subscribe Message:**
```json
{
  "type": "subscribe",
  "channels": ["contract_updates", "deployment_status"]
}
```

**Unsubscribe Message:**
```json
{
  "type": "unsubscribe",
  "channels": ["deployment_status"]
}
```

### Supported Events

- `contract_generated`: Contract generation completed
- `contract_validated`: Contract validation completed
- `deployment_started`: Contract deployment started
- `deployment_completed`: Contract deployment completed
- `deployment_failed`: Contract deployment failed
- `learning_insight`: New learning insight generated
- `system_update`: System status update

## Rate Limiting

The API implements rate limiting to ensure fair usage:

| Endpoint | Rate Limit | Window |
|----------|------------|--------|
| POST /contracts | 10 requests | 1 minute |
| POST /contracts/file | 5 requests | 1 minute |
| POST /contracts/*/deploy | 5 requests | 1 minute |
| POST /documentation/search | 30 requests | 1 minute |
| Other endpoints | 100 requests | 1 minute |

## Webhooks

### Setting up Webhooks

To receive webhook notifications, register your endpoint:

#### POST /webhooks
Register a webhook endpoint.

**Request Body:**
```json
{
  "url": "https://your-app.com/webhook",
  "events": ["contract_generated", "deployment_completed"],
  "secret": "your_webhook_secret"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "webhook_id": "webhook_id",
    "url": "https://your-app.com/webhook",
    "events": ["contract_generated", "deployment_completed"],
    "status": "active",
    "created_at": "2025-01-01T00:00:00Z"
  }
}
```

### Webhook Payload Format

```json
{
  "event": "contract_generated",
  "data": {
    "submission_id": "submission_id",
    "user_id": "user_id",
    "status": "COMPLETED"
  },
  "timestamp": "2025-01-01T00:00:00Z",
  "webhook_id": "webhook_id"
}
```

## SDK Examples

### Python SDK

```python
import requests
import json

class SmartContractLLMClient:
    def __init__(self, base_url="http://localhost:8000/api/v1"):
        self.base_url = base_url
        self.token = None

    def login(self, email, password):
        response = requests.post(f"{self.base_url}/users/login", json={
            'email': email,
            'password': password
        })
        data = response.json()
        self.token = data['data']['access_token']
        return data

    def generate_contract(self, content, network="testnet"):
        headers = {'Authorization': f'Bearer {self.token}'}
        response = requests.post(f"{self.base_url}/contracts", json={
            'input_type': 'NATURAL_LANGUAGE',
            'content': content,
            'network': network
        }, headers=headers)
        return response.json()

    def deploy_contract(self, submission_id, network="testnet"):
        headers = {'Authorization': f'Bearer {self.token}'}
        response = requests.post(
            f"{self.base_url}/contracts/{submission_id}/deploy",
            json={'network': network},
            headers=headers
        )
        return response.json()

# Usage
client = SmartContractLLMClient()
client.login('user@example.com', 'password')
result = client.generate_contract('Create a simple NFT contract')
submission_id = result['data']['submission_id']
deployment = client.deploy_contract(submission_id)
```

### JavaScript SDK

```javascript
class SmartContractLLMClient {
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

    async generateContract(content, network = 'testnet') {
        const response = await fetch(`${this.baseUrl}/contracts`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${this.token}`
            },
            body: JSON.stringify({
                input_type: 'NATURAL_LANGUAGE',
                content,
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
const client = new SmartContractLLMClient();
await client.login('user@example.com', 'password');
const result = await client.generateContract('Create a simple NFT contract');
const submissionId = result.data.submission_id;
const deployment = await client.deployContract(submissionId);
```
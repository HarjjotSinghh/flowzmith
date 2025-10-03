# IPFS Integration with Pinata

This document describes the IPFS storage integration using Pinata for storing smart contract code alongside PostgreSQL database storage.

## Overview

The Flowzmith platform now supports dual storage:
- **PostgreSQL Database**: Primary storage for contract metadata, configurations, and rapid access
- **IPFS (via Pinata)**: Decentralized storage for contract code, providing immutability and distributed access

## Installation

The integration uses the official Pinata Python package and additional dependencies:

```bash
pip install pinata>=0.0.1 tenacity>=8.2.0
```

## Configuration

Add the following environment variables to your `.env` file:

```bash
# IPFS Storage Configuration (Pinata)
ENABLE_IPFS_STORAGE=true
PINATA_JWT=your_pinata_jwt_token_here
PINATA_GATEWAY=your-gateway-subdomain.mypinata.cloud
```

### Getting Pinata Credentials

1. Sign up at [Pinata.cloud](https://pinata.cloud)
2. Go to API Keys section in your dashboard
3. Create a new API key with appropriate permissions:
   - `pinFileToIPFS` - for uploading files
   - `pinJSONToIPFS` - for uploading JSON data
   - `unpin` - for removing files
   - `pinList` - for listing pinned files
4. Copy the JWT token to `PINATA_JWT`
5. (Optional) Set up a dedicated gateway and add the subdomain to `PINATA_GATEWAY`

**Note**: The JWT token from Pinata's API Keys page is all you need. The integration uses Pinata's modern v3 API as documented in their [Python upload guide](https://pinata.cloud/blog/how-to-upload-to-ipfs-using-python/).

## Features

### Automatic IPFS Upload
- All generated contracts are automatically uploaded to IPFS when `ENABLE_IPFS_STORAGE=true`
- Contract code is stored with metadata including submission ID, user ID, and generation timestamp
- IPFS CID (Content Identifier) is stored in the database for quick retrieval

### Database Schema Updates
New fields added to `GeneratedConfiguration` model:
- `ipfs_cid`: IPFS Content Identifier
- `ipfs_pin_id`: Pinata pin ID for management
- `ipfs_uploaded_at`: Timestamp of IPFS upload
- `ipfs_metadata`: Additional IPFS metadata

### API Endpoints

#### IPFS Status
```
GET /api/v1/ipfs/status
```
Check IPFS service status and configuration.

#### Retrieve Contract from IPFS
```
GET /api/v1/ipfs/contract/{config_id}
```
Retrieve contract from IPFS by configuration ID.

#### Upload Contract to IPFS
```
POST /api/v1/ipfs/contract/{config_id}/upload
```
Manually upload an existing contract to IPFS.

#### List Contracts on IPFS
```
GET /api/v1/ipfs/contracts
```
List all contracts stored on IPFS with pagination.

#### Unpin Contract
```
DELETE /api/v1/ipfs/contract/{config_id}/unpin
```
Remove contract from IPFS storage (unpin from Pinata).

#### Sync Metadata
```
POST /api/v1/ipfs/contract/{config_id}/sync
```
Sync contract metadata from IPFS.

## Testing the Integration

A test script is provided to verify your IPFS integration:

```bash
# Make sure you're in the project directory and virtual environment is activated
source env/bin/activate

# Run the test script
python test_ipfs.py
```

The test script will:
1. Verify configuration settings
2. Test Pinata authentication
3. Upload a sample contract to IPFS
4. Retrieve the contract from IPFS
5. Verify content integrity

Example output:
```
🧪 Testing IPFS Integration with Pinata...
✅ IPFS storage enabled
✅ Pinata JWT configured
✅ Gateway: your-gateway.mypinata.cloud
✅ Pinata service initialized
✅ Pinata authentication successful
📤 Uploading test contract to IPFS...
✅ Contract uploaded successfully!
   CID: QmYourContentIdentifierHere
   Size: 1234 bytes
   Gateway URL: https://your-gateway.mypinata.cloud/ipfs/QmYourContentIdentifierHere
📥 Retrieving contract from IPFS...
✅ Contract retrieved successfully!
✅ Contract content matches original!
🎉 IPFS Integration Test PASSED!
```

## Usage Examples

### Check IPFS Service Status
```python
import requests

response = requests.get("http://localhost:8000/api/v1/ipfs/status")
print(response.json())
```

### Retrieve Contract from IPFS
```python
import requests

config_id = "your-config-id"
response = requests.get(f"http://localhost:8000/api/v1/ipfs/contract/{config_id}")
contract_data = response.json()

if contract_data["success"]:
    contract_code = contract_data["data"]["contract_code"]
    print(f"Contract code: {contract_code}")
```

### List All IPFS Contracts
```python
import requests

response = requests.get("http://localhost:8000/api/v1/ipfs/contracts")
contracts = response.json()

for contract in contracts:
    print(f"Config ID: {contract['config_id']}")
    print(f"IPFS CID: {contract['ipfs_cid']}")
    print(f"Gateway URL: {contract['gateway_url']}")
```

## Data Storage Strategy

### Primary Storage (PostgreSQL)
- Contract metadata and configurations
- User information and relationships
- Quick search and filtering capabilities
- Transactional consistency

### Secondary Storage (IPFS)
- Immutable contract code storage
- Decentralized access and distribution
- Content-addressed storage (CID-based)
- Backup and redundancy

### Fallback Mechanism
The system implements intelligent fallback:
1. First, try to retrieve contract code from PostgreSQL (fast)
2. If unavailable, fallback to IPFS retrieval (slower but reliable)
3. Log any retrieval issues for monitoring

## Benefits

### Immutability
- Contract code stored on IPFS is immutable and tamper-proof
- Content-addressed storage ensures data integrity

### Decentralization
- No single point of failure for contract storage
- Global accessibility through IPFS network

### Cost Efficiency
- Reduce database storage costs for large contract files
- Pinata provides reliable pinning service

### Compliance
- Immutable audit trail for contract code
- Decentralized storage for regulatory compliance

## Error Handling

The integration is designed to be non-blocking:
- If IPFS upload fails, contract generation continues
- Database operations are not affected by IPFS issues
- Comprehensive logging for troubleshooting

## Monitoring

Monitor IPFS integration health:
- Check `/api/v1/ipfs/status` endpoint regularly
- Monitor Pinata account usage and limits
- Track failed uploads in application logs

## Migration

To migrate existing contracts to IPFS:

1. Enable IPFS storage in configuration
2. Use the upload endpoint for each existing contract:
   ```bash
   curl -X POST "http://localhost:8000/api/v1/ipfs/contract/{config_id}/upload"
   ```
3. Verify uploads using the list endpoint
4. Update any external systems to use IPFS CIDs

## Troubleshooting

### Common Issues

1. **Authentication Failed**
   - Verify PINATA_JWT is correct and not expired
   - Check API key permissions in Pinata dashboard

2. **Gateway Not Accessible**
   - Verify PINATA_GATEWAY configuration
   - Ensure gateway is properly set up in Pinata

3. **Upload Failures**
   - Check Pinata account limits and usage
   - Verify network connectivity to Pinata API

4. **Retrieval Issues**
   - Check if content is properly pinned
   - Verify IPFS CID format and validity

### Debug Mode

Enable debug logging to troubleshoot issues:
```bash
LOG_LEVEL=DEBUG
```

This will provide detailed logs for all IPFS operations.

## Security Considerations

- IPFS content is public by default
- Sensitive contract information should be encrypted before upload
- Use private IPFS networks for confidential contracts
- Regularly rotate Pinata API keys
- Monitor access patterns to detect unauthorized usage

## Performance Considerations

- IPFS retrieval is slower than database access
- Implement caching for frequently accessed contracts
- Use background tasks for large batch uploads
- Monitor Pinata rate limits and plan accordingly

## Future Enhancements

- Encryption for sensitive contract data
- Integration with other IPFS providers
- Automatic contract versioning on IPFS
- Advanced metadata indexing and search
- Integration with Flow blockchain for contract verification

# Flow Testnet Testing

This directory contains test files for deploying and testing smart contracts on Flow Testnet.

## Prerequisites

### 1. Flow CLI Installation
Ensure you have Flow CLI installed:
```bash
sh -ci "$(curl -fsSL https://storage.googleapis.com/flow-cli/install.sh)"
```

### 2. Testnet Account Setup
You need a Flow Testnet account with FLOW tokens to run these tests.

#### Option A: Create Account via Flow CLI
```bash
flow accounts create --network testnet
```

#### Option B: Use Flow Wallet
1. Download [Flow Wallet](https://wallet.flow.com/)
2. Create a new wallet
3. Switch to Testnet network
4. Get your account address and private key

### 3. Get Testnet FLOW Tokens
Visit the [Flow Testnet Faucet](https://faucet.flow.com/) to get free testnet FLOW tokens.

### 4. Environment Variables
Set the following environment variables before running tests:

```bash
export FLOW_ACCOUNT_ADDRESS=0x1234567890abcdef  # Your testnet account address
export FLOW_PRIVATE_KEY=your_private_key_here   # Your testnet account private key
```

**Security Note**: Never commit real private keys to version control. Use environment variables or secure credential management.

## Test Files

### `test_complete_workflow_testnet.py`
Complete end-to-end test that:
- Creates a new Flow project
- Generates a unique test contract
- Deploys the contract to Flow Testnet
- Validates all required fields are returned
- Provides testnet explorer links for verification

## Running Tests

### Complete Workflow Test
```bash
cd /Users/harjjotsinghh/Desktop/Main/D Drive/Projects/smart-contract-llm
python tests/testnet/test_complete_workflow_testnet.py
```

### Environment Setup Script
```bash
# Set your testnet credentials
export FLOW_ACCOUNT_ADDRESS=0x1234567890abcdef
export FLOW_PRIVATE_KEY=your_private_key_here

# Run the test
python tests/testnet/test_complete_workflow_testnet.py
```

## Expected Output

A successful test run should show:
- ✅ Testnet credentials validation
- ✅ Project creation
- ✅ Contract deployment to testnet
- ✅ Transaction hash, contract address, and account address
- 🔗 Testnet explorer link for verification

## Troubleshooting

### Common Issues

1. **Missing Credentials**
   ```
   ❌ Missing required testnet credentials!
   ```
   **Solution**: Set `FLOW_ACCOUNT_ADDRESS` and `FLOW_PRIVATE_KEY` environment variables

2. **Insufficient FLOW Tokens**
   ```
   Error: insufficient funds
   ```
   **Solution**: Get more testnet FLOW from the [faucet](https://faucet.flow.com/)

3. **Network Connection Issues**
   ```
   Error: failed to connect to testnet
   ```
   **Solution**: Check internet connection and Flow Testnet status

4. **Invalid Private Key**
   ```
   Error: invalid signature
   ```
   **Solution**: Verify your private key is correct and matches your account

### Verification

After a successful deployment, you can verify your contract on:
- [Flow Testnet Explorer](https://testnet.flowscan.org/)
- Use the transaction hash provided in the test output

## Security Best Practices

1. **Never commit private keys** to version control
2. **Use environment variables** for sensitive data
3. **Test on testnet first** before mainnet deployment
4. **Keep testnet and mainnet credentials separate**
5. **Regularly rotate keys** for production accounts

## Support

For issues with:
- **Flow CLI**: [Flow CLI Documentation](https://developers.flow.com/tools/flow-cli)
- **Testnet**: [Flow Discord](https://discord.gg/flow)
- **This test suite**: Check the main project documentation
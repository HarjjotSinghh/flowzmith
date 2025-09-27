#!/bin/bash

# Flow Testnet Environment Setup Script
# This script helps you set up environment variables for testnet testing

echo "🔧 Flow Testnet Environment Setup"
echo "=================================="
echo ""

# Check if Flow CLI is installed
if ! command -v flow &> /dev/null; then
    echo "❌ Flow CLI is not installed!"
    echo "Please install it first:"
    echo "  sh -ci \"\$(curl -fsSL https://storage.googleapis.com/flow-cli/install.sh)\""
    exit 1
fi

echo "✅ Flow CLI is installed"
echo ""

# Function to validate Flow address format
validate_address() {
    local address=$1
    if [[ $address =~ ^0x[a-fA-F0-9]{16}$ ]]; then
        return 0
    else
        return 1
    fi
}

# Function to validate private key format (basic check)
validate_private_key() {
    local key=$1
    if [[ ${#key} -eq 64 ]] && [[ $key =~ ^[a-fA-F0-9]+$ ]]; then
        return 0
    else
        return 1
    fi
}

echo "Please provide your Flow Testnet credentials:"
echo ""

# Get account address
while true; do
    read -p "Enter your testnet account address (0x...): " FLOW_ACCOUNT_ADDRESS
    if validate_address "$FLOW_ACCOUNT_ADDRESS"; then
        break
    else
        echo "❌ Invalid address format. Please use format: 0x1234567890abcdef"
    fi
done

echo ""

# Get private key
while true; do
    read -s -p "Enter your testnet private key (64 hex characters): " FLOW_PRIVATE_KEY
    echo ""
    if validate_private_key "$FLOW_PRIVATE_KEY"; then
        break
    else
        echo "❌ Invalid private key format. Please enter 64 hexadecimal characters."
    fi
done

echo ""

# Create .env file for this session
ENV_FILE="$(dirname "$0")/.env.testnet"
cat > "$ENV_FILE" << EOF
# Flow Testnet Environment Variables
# Generated on $(date)
export FLOW_ACCOUNT_ADDRESS=$FLOW_ACCOUNT_ADDRESS
export FLOW_PRIVATE_KEY=$FLOW_PRIVATE_KEY
EOF

echo "✅ Environment variables saved to: $ENV_FILE"
echo ""

# Set variables for current session
export FLOW_ACCOUNT_ADDRESS
export FLOW_PRIVATE_KEY

echo "✅ Environment variables set for current session:"
echo "  FLOW_ACCOUNT_ADDRESS: $FLOW_ACCOUNT_ADDRESS"
echo "  FLOW_PRIVATE_KEY: ${FLOW_PRIVATE_KEY:0:8}...${FLOW_PRIVATE_KEY: -8}"
echo ""

# Check testnet connection
echo "🔍 Testing connection to Flow Testnet..."
if flow accounts get "$FLOW_ACCOUNT_ADDRESS" --network testnet &> /dev/null; then
    echo "✅ Successfully connected to testnet account!"
    
    # Get account balance
    echo "💰 Checking account balance..."
    BALANCE=$(flow accounts get "$FLOW_ACCOUNT_ADDRESS" --network testnet | grep -o "Balance: [0-9.]*" | cut -d' ' -f2)
    if [ -n "$BALANCE" ]; then
        echo "  Account Balance: $BALANCE FLOW"
        
        # Check if balance is sufficient for testing
        if (( $(echo "$BALANCE < 1.0" | bc -l) )); then
            echo "⚠️  Low balance detected. You may need more FLOW tokens."
            echo "   Visit the testnet faucet: https://faucet.flow.com/"
        else
            echo "✅ Sufficient balance for testing"
        fi
    fi
else
    echo "❌ Failed to connect to testnet account"
    echo "   Please verify your credentials and network connectivity"
fi

echo ""
echo "🚀 Setup complete! You can now run testnet tests:"
echo "   source $ENV_FILE"
echo "   python tests/testnet/test_complete_workflow_testnet.py"
echo ""
echo "💡 To use these variables in future sessions:"
echo "   source $ENV_FILE"
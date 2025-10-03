#!/bin/bash

# Script to sync generated Python schema to backend
# Usage: ./scripts/sync-schema-to-backend.sh

set -e

echo "🔄 Syncing schema to backend..."

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Step 1: Generate Python types
echo -e "${BLUE}📝 Generating Python types...${NC}"
cd monorepo/packages/flowzmith-schema
npm run generate-python

# Step 2: Copy to backend
echo -e "${BLUE}📋 Copying to backend...${NC}"
cd ../../..
mkdir -p src/models
cp monorepo/packages/flowzmith-schema/python/schema.py src/models/flowzmith_schema.py

# Step 3: Create __init__.py if it doesn't exist
if [ ! -f src/models/__init__.py ]; then
    echo "from .flowzmith_schema import *" > src/models/__init__.py
fi

echo -e "${GREEN}✅ Schema synced successfully!${NC}"
echo ""
echo "You can now import types in your backend:"
echo "  from src.models.flowzmith_schema import CreateContractRequest, CreateContractResponse"
echo ""
echo "Or use the shorthand:"
echo "  from src.models import CreateContractRequest, CreateContractResponse"

# CLI Workspace Setup Guide

## Quick Start

### 1. Install Dependencies

```bash
cd flowZmith
npm install
```

### 2. Install Flow CLI

The Flow CLI is required for compilation and deployment features.

**macOS/Linux:**
```bash
sh -ci "$(curl -fsSL https://raw.githubusercontent.com/onflow/flow-cli/master/install.sh)"
```

**Windows:**
```powershell
iex "& { $(irm 'https://raw.githubusercontent.com/onflow/flow-cli/master/install.ps1') }"
```

Verify installation:
```bash
flow version
```

### 3. Configure Environment Variables

Copy the example environment file:
```bash
cp .env.example .env.local
```

Edit `.env.local` with your configuration:

```env
# Backend API URL (Python FastAPI server)
BACKEND_URL=http://localhost:8000

# Next.js App URL
NEXT_PUBLIC_APP_URL=http://localhost:3001

# GitHub OAuth (optional - for GitHub integration)
GITHUB_CLIENT_ID=your_github_client_id
GITHUB_CLIENT_SECRET=your_github_client_secret
```

### 4. Set Up GitHub OAuth (Optional)

If you want to use the "Push to GitHub" feature:

1. Go to [GitHub Developer Settings](https://github.com/settings/developers)
2. Click "New OAuth App"
3. Fill in the details:
   - **Application name**: Flowzmith CLI
   - **Homepage URL**: `http://localhost:3001`
   - **Authorization callback URL**: `http://localhost:3001/api/auth/github/callback`
4. Click "Register application"
5. Copy the **Client ID** and **Client Secret**
6. Add them to your `.env.local` file

### 5. Start the Backend Server

The Python backend must be running for contract generation and deployment:

```bash
# In the root directory
python -m uvicorn src.main:app --reload --port 8000
```

Or using Docker:
```bash
docker-compose up
```

### 6. Start the Frontend

```bash
cd flowZmith
npm run dev
```

The application will be available at `http://localhost:3001`

## Testing the Features

### Test Contract Generation

1. Navigate to `http://localhost:3001/cli`
2. Click "Create Contract" in the sidebar
3. Fill in:
   - **Contract Name**: TestContract
   - **Description**: A test smart contract
4. Click "Execute"
5. Wait for generation to complete
6. Files should appear in the left sidebar

### Test File Explorer

1. After generation, you should see a file tree
2. Click folders to expand/collapse
3. Click files to open them in the editor
4. The main contract should open automatically

### Test Export

1. Click the "Export" dropdown button
2. Select "Export as .zip"
3. A ZIP file should download
4. Extract and verify all files are present

### Test Compilation

1. Select a `.cdc` file in the file tree
2. Click the "Compile" button
3. Check the Terminal tab for results
4. Should show "Contract compiled successfully"

### Test Deployment

1. Ensure Flow CLI is installed
2. Select a `.cdc` file
3. Click "Deploy On-Chain"
4. Monitor progress in Terminal tab
5. Should show transaction ID on success

### Test GitHub Integration

1. Ensure GitHub OAuth is configured
2. Click "Push to GitHub"
3. Authenticate with GitHub (first time)
4. Repository should be created
5. Browser opens to new repository

## Troubleshooting

### Backend Connection Issues

**Error**: "Failed to fetch project files"

**Solution**:
```bash
# Check if backend is running
curl http://localhost:8000/health

# If not running, start it
python -m uvicorn src.main:app --reload --port 8000
```

### Flow CLI Issues

**Error**: "flow: command not found"

**Solution**:
```bash
# Reinstall Flow CLI
sh -ci "$(curl -fsSL https://raw.githubusercontent.com/onflow/flow-cli/master/install.sh)"

# Add to PATH (if needed)
export PATH="$PATH:$HOME/.local/bin"
```

### GitHub OAuth Issues

**Error**: "GitHub OAuth not configured"

**Solution**:
1. Verify `GITHUB_CLIENT_ID` and `GITHUB_CLIENT_SECRET` in `.env.local`
2. Restart the Next.js dev server
3. Clear browser cookies and try again

### Port Conflicts

**Error**: "Port 3001 already in use"

**Solution**:
```bash
# Use a different port
npm run dev -- --port 3002

# Update NEXT_PUBLIC_APP_URL in .env.local
NEXT_PUBLIC_APP_URL=http://localhost:3002
```

## Development Tips

### Hot Reload

The application supports hot reload for:
- React components
- API routes
- Environment variables (requires restart)

### Debugging

Enable verbose logging:
```env
# Add to .env.local
DEBUG=true
LOG_LEVEL=debug
```

View logs in:
- Browser console (frontend)
- Terminal (backend)
- Terminal tab in UI (operations)

### Testing API Endpoints

Use curl or Postman to test API endpoints:

```bash
# Test file fetching
curl "http://localhost:3001/api/projects/files?path=flow_projects/test-project"

# Test compilation
curl -X POST http://localhost:3001/api/contracts/compile \
  -H "Content-Type: application/json" \
  -d '{"contract_code":"pub contract Test {}","contract_name":"Test"}'
```

## Production Deployment

### Environment Variables

Update for production:
```env
BACKEND_URL=https://api.yourapp.com
NEXT_PUBLIC_APP_URL=https://yourapp.com
GITHUB_CLIENT_ID=prod_client_id
GITHUB_CLIENT_SECRET=prod_client_secret
NODE_ENV=production
```

### Build

```bash
npm run build
npm start
```

### Docker

```bash
docker build -t flowzmith-frontend .
docker run -p 3001:3001 flowzmith-frontend
```

## Security Checklist

- [ ] Environment variables are not committed to git
- [ ] GitHub OAuth secrets are secure
- [ ] HTTPS is enabled in production
- [ ] CORS is properly configured
- [ ] File access is restricted to allowed directories
- [ ] Input validation is enabled on all endpoints
- [ ] Rate limiting is configured
- [ ] Authentication is required for sensitive operations

## Next Steps

1. Explore the [CLI Workspace Features](./CLI_WORKSPACE_FEATURES.md) documentation
2. Check out the [API Documentation](./API_DOCUMENTATION.md)
3. Review the [Architecture Overview](./ARCHITECTURE.md)
4. Join our [Discord community](https://discord.gg/flowzmith)

## Support

- **Documentation**: [docs.flowzmith.com](https://docs.flowzmith.com)
- **Issues**: [GitHub Issues](https://github.com/flowzmith/flowzmith/issues)
- **Discord**: [Join our community](https://discord.gg/flowzmith)
- **Email**: support@flowzmith.com

# CLI Workspace Features

## Overview

The CLI Workspace provides a complete IDE-like experience for Flow smart contract development directly in the browser. After generating contracts, you can view, edit, compile, and deploy them without leaving the application.

## Features

### 1. Project File Explorer

- **Tree View**: Navigate through your generated project structure
- **Folder Expansion**: Click folders to expand/collapse
- **File Selection**: Click files to open them in the editor
- **Real-time Updates**: Files are loaded immediately after generation

### 2. Monaco Code Editor

- **Syntax Highlighting**: Full support for Cadence (.cdc), JSON, and other file types
- **Code Editing**: Edit contracts directly in the browser
- **Dark Theme**: Professional dark theme for comfortable coding
- **Auto-save**: Changes are preserved in the current session

### 3. Export Options

#### Export as ZIP
- Downloads all project files as a compressed .zip archive
- Preserves folder structure
- Ready to extract and use locally

#### Export as TAR
- Downloads project as a .tar archive
- Alternative format for Unix-based systems

### 4. GitHub Integration

#### Push to GitHub
1. Click "Push to GitHub" button
2. Authenticate with GitHub OAuth (first time only)
3. Repository is automatically created with your project name
4. All files are uploaded to the repository
5. Repository opens in a new tab

**Setup Required:**
```bash
# Add to .env.local
GITHUB_CLIENT_ID=your_github_oauth_app_client_id
GITHUB_CLIENT_SECRET=your_github_oauth_app_client_secret
NEXT_PUBLIC_APP_URL=http://localhost:3001
```

**Create GitHub OAuth App:**
1. Go to GitHub Settings → Developer settings → OAuth Apps
2. Click "New OAuth App"
3. Set Authorization callback URL to: `http://localhost:3001/api/auth/github/callback`
4. Copy Client ID and Client Secret to .env.local

### 5. Compile Contract

- **Syntax Checking**: Validates Cadence syntax using Flow CLI
- **Error Reporting**: Shows compilation errors in the terminal
- **Warnings**: Displays any warnings from the compiler
- **Only for .cdc files**: Button appears only when a Cadence file is selected

**Requirements:**
- Flow CLI must be installed and available in PATH
- Run: `sh -ci "$(curl -fsSL https://raw.githubusercontent.com/onflow/flow-cli/master/install.sh)"`

### 6. Deploy On-Chain

- **Network Selection**: Deploy to testnet, mainnet, or emulator
- **Automatic Deployment**: Uses Flow CLI to deploy contracts
- **Transaction Tracking**: Shows transaction ID after deployment
- **Contract Address**: Displays deployed contract address
- **Real-time Logs**: View deployment progress in terminal

**Requirements:**
- Flow CLI installed
- Flow account configured in flow.json
- Network access (for testnet/mainnet)

## User Interface

### Action Toolbar

Located above the editor, the toolbar provides quick access to all actions:

```
[Export ▼] [Push to GitHub] | [Compile] [Deploy On-Chain]
```

- **Export Dropdown**: Choose between .zip and .tar formats
- **GitHub Button**: One-click repository creation
- **Compile Button**: Validate contract syntax (only for .cdc files)
- **Deploy Button**: Deploy to blockchain (only for .cdc files)

### Loading States

All actions show appropriate loading indicators:
- Spinning loader icon during processing
- Disabled buttons to prevent duplicate actions
- Status messages in terminal output

### Terminal Output

The terminal tab shows real-time logs for all operations:
- Command execution
- API calls
- File operations
- Compilation results
- Deployment status
- Error messages

## API Endpoints

### Frontend (Next.js)

#### GET `/api/projects/files`
Fetch all files from a generated project.

**Query Parameters:**
- `path`: Project path (e.g., `flow_projects/abc123`)

**Response:**
```json
{
  "files": [
    {
      "name": "Contract.cdc",
      "path": "contracts/Contract.cdc",
      "type": "file",
      "content": "pub contract..."
    }
  ]
}
```

#### POST `/api/contracts/compile`
Compile a Cadence contract.

**Request:**
```json
{
  "contract_code": "pub contract MyContract { ... }",
  "contract_name": "MyContract"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Contract compiled successfully",
  "output": "...",
  "warnings": []
}
```

#### POST `/api/contracts/deploy`
Deploy a contract to the blockchain.

**Request:**
```json
{
  "project_path": "flow_projects/abc123",
  "contract_name": "MyContract",
  "network": "testnet"
}
```

**Response:**
```json
{
  "success": true,
  "transaction_id": "0x...",
  "contract_address": "0x..."
}
```

#### GET `/api/auth/github`
Initiate GitHub OAuth flow.

**Query Parameters:**
- `redirect`: URL to redirect after authentication

#### POST `/api/github/create-repo`
Create a GitHub repository with project files.

**Request:**
```json
{
  "repo_name": "my-flow-project",
  "description": "Flow smart contract project",
  "files": [
    {
      "path": "contracts/Contract.cdc",
      "content": "..."
    }
  ],
  "is_private": false
}
```

**Response:**
```json
{
  "success": true,
  "repo_url": "https://github.com/user/my-flow-project",
  "repo_name": "user/my-flow-project"
}
```

### Backend (Python/FastAPI)

The frontend proxies deployment requests to the Python backend at `/api/v1/flow/deploy`.

## Workflow Example

### Complete Development Cycle

1. **Generate Contract**
   - Click "Create Contract" in sidebar
   - Fill in contract details
   - Click "Execute"
   - Wait for generation to complete

2. **View Files**
   - Project files appear in left sidebar
   - Main contract opens automatically in editor
   - Explore other generated files (transactions, scripts, tests)

3. **Edit Contract**
   - Make changes in Monaco editor
   - Syntax highlighting helps with Cadence syntax
   - Changes are saved in current session

4. **Compile**
   - Click "Compile" button
   - View results in Terminal tab
   - Fix any errors shown

5. **Deploy**
   - Click "Deploy On-Chain" button
   - Monitor deployment in Terminal
   - Note transaction ID and contract address

6. **Export**
   - Click "Export" dropdown
   - Choose .zip or .tar format
   - Download starts automatically

7. **Share on GitHub**
   - Click "Push to GitHub"
   - Authenticate (first time only)
   - Repository created automatically
   - View on GitHub

## Troubleshooting

### Compilation Fails

**Error**: "Flow CLI not found"
- **Solution**: Install Flow CLI: `sh -ci "$(curl -fsSL https://raw.githubusercontent.com/onflow/flow-cli/master/install.sh)"`

**Error**: "Syntax error in contract"
- **Solution**: Check Terminal output for specific error location and fix syntax

### Deployment Fails

**Error**: "No account configured"
- **Solution**: Ensure flow.json has valid account configuration

**Error**: "Network connection failed"
- **Solution**: Check internet connection and network status

### GitHub Export Fails

**Error**: "Not authenticated with GitHub"
- **Solution**: Click "Push to GitHub" again to re-authenticate

**Error**: "Repository already exists"
- **Solution**: Repository name is auto-generated. Delete existing repo or rename

### Files Not Loading

**Error**: "Project not found"
- **Solution**: Ensure contract generation completed successfully

**Error**: "Access denied"
- **Solution**: Project path must be within `flow_projects` directory

## Security Considerations

1. **Path Traversal Protection**: File access is restricted to `flow_projects` directory
2. **OAuth Tokens**: GitHub tokens stored in httpOnly cookies
3. **Input Validation**: All API inputs are validated
4. **Temporary Files**: Compilation uses temporary directories that are cleaned up

## Performance

- **File Loading**: Asynchronous loading with progress indicators
- **Editor**: Monaco editor loads dynamically (code splitting)
- **Export**: Client-side ZIP generation (no server load)
- **GitHub**: Parallel file uploads for faster repository creation

## Future Enhancements

- [ ] Multi-file editing with tabs
- [ ] Git integration (commit, push, pull)
- [ ] Collaborative editing
- [ ] Contract testing in browser
- [ ] Deployment to multiple networks simultaneously
- [ ] Contract verification
- [ ] Version control integration
- [ ] Code snippets and templates
- [ ] AI-powered code suggestions

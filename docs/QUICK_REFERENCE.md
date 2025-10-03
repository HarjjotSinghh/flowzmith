# CLI Workspace Quick Reference

## Quick Commands

### Start Development
```bash
# Terminal 1: Backend
python -m uvicorn src.main:app --reload --port 8000

# Terminal 2: Frontend
cd flowZmith && npm run dev
```

### Environment Setup
```bash
cp .env.example .env.local
# Edit .env.local with your values
```

### Install Flow CLI
```bash
sh -ci "$(curl -fsSL https://raw.githubusercontent.com/onflow/flow-cli/master/install.sh)"
```

## Key Files

| File | Purpose |
|------|---------|
| `app/cli/page.tsx` | Main CLI workspace component |
| `app/api/projects/files/route.ts` | Fetch project files |
| `app/api/contracts/compile/route.ts` | Compile contracts |
| `app/api/contracts/deploy/route.ts` | Deploy contracts |
| `app/api/github/create-repo/route.ts` | Create GitHub repos |
| `components/cli/cli-sidebar.tsx` | Command sidebar |
| `components/cli/command-dialog.tsx` | Command input dialog |
| `components/cli/terminal-output.tsx` | Terminal logs |

## API Endpoints

### GET `/api/projects/files`
```bash
curl "http://localhost:3001/api/projects/files?path=flow_projects/abc123"
```

### POST `/api/contracts/compile`
```bash
curl -X POST http://localhost:3001/api/contracts/compile \
  -H "Content-Type: application/json" \
  -d '{"contract_code":"pub contract Test {}","contract_name":"Test"}'
```

### POST `/api/contracts/deploy`
```bash
curl -X POST http://localhost:3001/api/contracts/deploy \
  -H "Content-Type: application/json" \
  -d '{"project_path":"flow_projects/abc123","contract_name":"Test","network":"testnet"}'
```

### POST `/api/github/create-repo`
```bash
curl -X POST http://localhost:3001/api/github/create-repo \
  -H "Content-Type: application/json" \
  -H "Cookie: github_access_token=YOUR_TOKEN" \
  -d '{"repo_name":"my-project","files":[...]}'
```

## Component Props

### CLISidebar
```typescript
interface CLISidebarProps {
  onCommandSelect: (command: CLICommand) => void
  selectedCommand?: CLICommand | null
  className?: string
}
```

### CommandDialog
```typescript
interface CommandDialogProps {
  command: CLICommand | null
  open: boolean
  onOpenChange: (open: boolean) => void
  onExecute: (command: CLICommand, data: any) => Promise<any>
}
```

### TerminalOutput
```typescript
interface TerminalOutputProps {
  logs: TerminalLog[]
  isStreaming: boolean
  onClear: () => void
  className?: string
}
```

## State Management

### Main State Variables
```typescript
const [selectedCommand, setSelectedCommand] = useState<CLICommand | null>(null)
const [dialogOpen, setDialogOpen] = useState(false)
const [files, setFiles] = useState<FileNode[]>([])
const [selectedFile, setSelectedFile] = useState<FileNode | null>(null)
const [projectData, setProjectData] = useState<ProjectData | null>(null)
const [expandedFolders, setExpandedFolders] = useState<Set<string>>(new Set())
const [isLoading, setIsLoading] = useState(false)
const [isCompiling, setIsCompiling] = useState(false)
const [isDeploying, setIsDeploying] = useState(false)
const [isExporting, setIsExporting] = useState(false)
```

## Common Tasks

### Add New Command
1. Edit `config/cli-commands.json`
2. Add command definition
3. Add icon to `cli-sidebar.tsx` iconMap
4. Implement handler in `page.tsx`

### Add New API Endpoint
1. Create `app/api/[route]/route.ts`
2. Implement GET/POST handler
3. Add error handling
4. Update documentation

### Modify File Tree
1. Update `FileNode` interface
2. Modify `buildFileTree()` function
3. Update `renderFileTree()` rendering
4. Test with nested folders

### Add Export Format
1. Add to Export dropdown menu
2. Implement handler function
3. Add file generation logic
4. Test download

## Debugging

### Enable Verbose Logging
```typescript
// In page.tsx
console.log('Debug:', { files, selectedFile, projectData })
```

### Check API Responses
```typescript
// In API route
console.log('Request:', await request.json())
console.log('Response:', result)
```

### Monitor Terminal Logs
```typescript
// Use addLog function
addLog('Debug message', 'info')
addLog('Warning message', 'warning')
addLog('Error message', 'error')
addLog('Success message', 'success')
```

## Common Issues

### Files Not Loading
```typescript
// Check project path
console.log('Project path:', projectData?.projectPath)

// Verify API response
const response = await fetch(`/api/projects/files?path=${projectPath}`)
console.log('Files:', await response.json())
```

### Compilation Fails
```bash
# Check Flow CLI
flow version

# Test manually
flow cadence check Contract.cdc
```

### GitHub OAuth Not Working
```bash
# Verify environment variables
echo $GITHUB_CLIENT_ID
echo $GITHUB_CLIENT_SECRET

# Check callback URL
# Should be: http://localhost:3001/api/auth/github/callback
```

## Testing Checklist

- [ ] Generate contract
- [ ] View file tree
- [ ] Expand/collapse folders
- [ ] Open file in editor
- [ ] Edit file content
- [ ] Export as ZIP
- [ ] Export as TAR
- [ ] Compile contract
- [ ] Deploy contract
- [ ] Push to GitHub
- [ ] Check terminal logs
- [ ] Verify error handling

## Performance Tips

### Optimize File Loading
```typescript
// Use pagination for large projects
const BATCH_SIZE = 50
const files = await fetchFilesBatch(projectPath, 0, BATCH_SIZE)
```

### Lazy Load Editor
```typescript
// Already implemented
const Editor = dynamic(() => import("@monaco-editor/react"), { ssr: false })
```

### Cache File Contents
```typescript
const fileCache = new Map<string, string>()
const content = fileCache.get(filePath) || await fetchFile(filePath)
```

## Security Checklist

- [ ] Path traversal protection enabled
- [ ] OAuth tokens in httpOnly cookies
- [ ] Input validation on all endpoints
- [ ] CORS properly configured
- [ ] Rate limiting implemented
- [ ] Error messages don't leak sensitive info
- [ ] File access restricted to allowed directories

## Deployment Checklist

- [ ] Environment variables set
- [ ] GitHub OAuth configured
- [ ] Flow CLI installed
- [ ] Database connected
- [ ] Backend running
- [ ] Frontend built
- [ ] HTTPS enabled (production)
- [ ] Monitoring configured

## Useful Links

- [Flow CLI Docs](https://developers.flow.com/tools/flow-cli)
- [Monaco Editor API](https://microsoft.github.io/monaco-editor/api/index.html)
- [GitHub OAuth Guide](https://docs.github.com/en/developers/apps/building-oauth-apps)
- [Next.js API Routes](https://nextjs.org/docs/api-routes/introduction)
- [JSZip Documentation](https://stuk.github.io/jszip/)

## Support

- **Issues**: Create GitHub issue with logs
- **Questions**: Ask in Discord #support
- **Bugs**: Include reproduction steps
- **Features**: Submit feature request

## Version Info

- **Current Version**: 1.0.0
- **Last Updated**: 2025-10-03
- **Node Version**: 18+
- **Next.js Version**: 15.2.4
- **React Version**: 19

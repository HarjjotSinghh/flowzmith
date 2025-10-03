# Setup Guide: CLI Integration with Frontend

This guide will help you set up the centralized CLI integration in your Flowzmith application.

## Prerequisites

- Node.js >= 18
- Bun >= 1.1.0 (or npm/yarn)
- Python >= 3.8 (for backend)
- Running FastAPI backend

## Step 1: Install Dependencies

### Install Schema Package

```bash
# From monorepo root
cd monorepo/packages/flowzmith-schema
bun install
bun run build
```

### Install Frontend Dependencies

```bash
cd monorepo/apps/app/app
bun install
```

The following packages should already be installed:
- `@monaco-editor/react` - Code editor
- `@radix-ui/*` - UI components
- `react-hook-form` - Form handling
- `@hookform/resolvers` - Form validation
- `zod` - Schema validation

## Step 2: Link Schema Package

### Option A: Using Workspace (Recommended)

The schema package is already in the workspace. Just build it:

```bash
cd monorepo/packages/flowzmith-schema
bun run build
```

### Option B: Manual Link

```bash
cd monorepo/packages/flowzmith-schema
bun link

cd monorepo/apps/app/app
bun link @flowzmith/schema
```

## Step 3: Configure Environment Variables

Create or update `.env.local` in `monorepo/apps/app/app/`:

```env
# API Configuration
NEXT_PUBLIC_API_URL=http://localhost:8000

# Optional: For production
# NEXT_PUBLIC_API_URL=https://api.flowzmith.com
```

## Step 4: Update Backend to Use Schema

### Install Python Package (Future)

For now, copy the generated Python types:

```bash
# Copy generated Python types to backend
cp monorepo/packages/flowzmith-schema/python/schema.py src/models/schema.py
```

### Update Backend Imports

```python
# In your FastAPI endpoints
from src.models.schema import (
    CreateContractRequest,
    CreateContractResponse,
    DeployContractRequest,
    DeployContractResponse
)

@app.post("/api/contracts/submit")
async def create_contract(request: CreateContractRequest) -> CreateContractResponse:
    # Your implementation
    pass
```

## Step 5: Start Development Servers

### Terminal 1: Backend

```bash
python -m uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
```

### Terminal 2: Frontend

```bash
cd monorepo/apps/app/app
bun run dev
```

### Terminal 3: Schema Watcher (Optional)

```bash
cd monorepo/packages/flowzmith-schema
bun run dev
```

## Step 6: Access the CLI Interface

1. Open your browser to `http://localhost:3000`
2. Navigate to `/dashboard/cli`
3. You should see the CLI sidebar with all commands

## Step 7: Test the Integration

### Test 1: Create Contract

1. Click "Create Contract" in the sidebar
2. Fill in the requirements
3. Select network (emulator/testnet/mainnet)
4. Click "Execute"
5. View generated contract in the editor

### Test 2: List Deployments

1. Click "List Deployments" in the sidebar
2. Click "Execute"
3. View deployment history

### Test 3: System Status

1. Click "System Status" in the sidebar
2. Click "Execute"
3. View system statistics

## Troubleshooting

### Issue: Schema package not found

**Solution**:
```bash
cd monorepo/packages/flowzmith-schema
bun install
bun run build
cd ../../apps/app/app
bun install
```

### Issue: API connection failed

**Solution**:
1. Check backend is running: `curl http://localhost:8000/health`
2. Verify `NEXT_PUBLIC_API_URL` in `.env.local`
3. Check CORS settings in backend

### Issue: TypeScript errors

**Solution**:
```bash
# Rebuild schema package
cd monorepo/packages/flowzmith-schema
bun run build

# Clear Next.js cache
cd monorepo/apps/app/app
rm -rf .next
bun run dev
```

### Issue: Monaco Editor not loading

**Solution**:
```bash
cd monorepo/apps/app/app
bun add @monaco-editor/react
```

### Issue: UI components missing

**Solution**:
```bash
cd monorepo/apps/app/app
bun add @radix-ui/react-dialog @radix-ui/react-scroll-area @radix-ui/react-tabs
```

## Project Structure

```
monorepo/
├── packages/
│   └── flowzmith-schema/          # Centralized schema
│       ├── src/
│       │   └── index.ts           # TypeScript definitions
│       ├── python/
│       │   └── schema.py          # Generated Python types
│       └── package.json
│
├── apps/
│   └── app/
│       └── app/
│           ├── app/
│           │   └── dashboard/
│           │       └── cli/
│           │           └── page.tsx    # CLI workspace page
│           ├── components/
│           │   ├── cli-sidebar.tsx     # Command sidebar
│           │   ├── command-dialog.tsx  # Command execution dialog
│           │   └── ui/                 # UI components
│           └── lib/
│               └── api-client.ts       # API client
│
└── cli.py                              # Original CLI (reference)
```

## Adding New Commands

### 1. Define in Schema

Edit `monorepo/packages/flowzmith-schema/src/index.ts`:

```typescript
// Add to CLICommandType enum
export const CLICommandType = z.enum([
  // ... existing commands
  "my_new_command",
])

// Define request schema
export const MyNewCommandRequestSchema = z.object({
  param1: z.string(),
  param2: z.number().optional(),
})

export type MyNewCommandRequest = z.infer<typeof MyNewCommandRequestSchema>

// Add to CLI_COMMANDS array
{
  id: "my_new_command",
  name: "My New Command",
  description: "Does something awesome",
  icon: "Sparkles",
  category: "contract",
  requiresInput: true,
  steps: [
    {
      id: "input",
      title: "Input Parameters",
      fields: [
        {
          name: "param1",
          label: "Parameter 1",
          type: "text",
          required: true,
        }
      ]
    }
  ]
}
```

### 2. Generate Python Types

```bash
cd monorepo/packages/flowzmith-schema
bun run generate-python
```

### 3. Implement Backend Endpoint

```python
from src.models.schema import MyNewCommandRequest

@app.post("/api/my-new-command")
async def my_new_command(request: MyNewCommandRequest):
    # Implementation
    return {"status": "success"}
```

### 4. Add to Frontend API Client

Edit `monorepo/apps/app/app/lib/api-client.ts`:

```typescript
async myNewCommand(data: MyNewCommandRequest): Promise<any> {
  return this.request("/api/my-new-command", {
    method: "POST",
    body: JSON.stringify(data),
  })
}
```

### 5. Add Handler in CLI Page

Edit `monorepo/apps/app/app/app/dashboard/cli/page.tsx`:

```typescript
const handleExecuteCommand = async (command: CLICommand, data: any) => {
  // ... existing cases
  case "my_new_command":
    result = await apiClient.myNewCommand(data)
    break
}
```

### 6. Test

1. Rebuild schema: `bun run build`
2. Restart frontend: `bun run dev`
3. Navigate to `/dashboard/cli`
4. Your new command appears in the sidebar!

## Production Deployment

### 1. Build Schema Package

```bash
cd monorepo/packages/flowzmith-schema
bun run build
bun run generate-python
```

### 2. Build Frontend

```bash
cd monorepo/apps/app/app
bun run build
```

### 3. Deploy Backend

```bash
# Copy Python types
cp monorepo/packages/flowzmith-schema/python/schema.py src/models/

# Deploy with your preferred method
docker build -t flowzmith-backend .
```

### 4. Environment Variables

Set in production:
```env
NEXT_PUBLIC_API_URL=https://api.flowzmith.com
```

## Next Steps

1. **Add Authentication**: Protect CLI endpoints with auth
2. **Add Streaming**: Implement real-time progress updates
3. **Add File Upload**: Support uploading context files
4. **Add Export**: Export generated contracts as ZIP
5. **Add History**: Persist execution history in database

## Resources

- [Architecture Documentation](./CENTRALIZED_SCHEMA_ARCHITECTURE.md)
- [Schema Package README](./monorepo/packages/flowzmith-schema/README.md)
- [Zod Documentation](https://zod.dev/)
- [Radix UI](https://www.radix-ui.com/)
- [Monaco Editor](https://microsoft.github.io/monaco-editor/)

## Support

If you encounter issues:
1. Check the troubleshooting section above
2. Review the architecture documentation
3. Check backend logs: `tail -f server.log`
4. Check frontend console for errors
5. Verify all services are running

## Summary

You now have:
- ✅ Centralized schema package
- ✅ Type-safe API contracts
- ✅ CLI commands in frontend UI
- ✅ Multi-step command dialogs
- ✅ Code editor for viewing results
- ✅ Execution history tracking
- ✅ Python type generation

All CLI functionality is now accessible through a beautiful web interface!

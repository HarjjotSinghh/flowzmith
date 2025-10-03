# Quick Reference - CLI Frontend Integration

## 🚀 Quick Start

```bash
# Build schema package
cd monorepo/packages/flowzmith-schema && npm run build

# Start frontend
cd monorepo/apps/app/app && npm run dev

# Visit
open http://localhost:3000/dashboard/cli
```

## 📁 Key Files

| File | Purpose |
|------|---------|
| `monorepo/packages/flowzmith-schema/src/index.ts` | Schema definitions |
| `monorepo/apps/app/app/components/cli-sidebar.tsx` | Command sidebar |
| `monorepo/apps/app/app/components/command-dialog.tsx` | Command dialog |
| `monorepo/apps/app/app/app/dashboard/cli/page.tsx` | CLI workspace |
| `monorepo/apps/app/app/lib/api-client.ts` | API client |

## 🎯 Common Tasks

### Add New Command

```typescript
// 1. In schema package (src/index.ts)
{
  id: "my_command",
  name: "My Command",
  description: "Description",
  icon: "Sparkles",
  category: "contract",
  requiresInput: true,
  steps: [...]
}

// 2. Generate Python types
npm run generate-python

// 3. Implement backend
@app.post("/api/my-command")
async def my_command(request: MyCommandRequest):
    return {"status": "success"}

// 4. Add to API client
async myCommand(data: MyCommandRequest) {
  return this.request("/api/my-command", ...)
}
```

### Update Existing Command

```typescript
// 1. Edit in schema package
// 2. Rebuild: npm run build
// 3. Regenerate Python: npm run generate-python
// 4. Update backend if needed
```

### Sync Schema to Backend

```bash
./scripts/sync-schema-to-backend.sh
```

## 🔧 Development Commands

```bash
# Schema package
cd monorepo/packages/flowzmith-schema
npm run build              # Build package
npm run dev                # Watch mode
npm run generate-python    # Generate Python types

# Frontend
cd monorepo/apps/app/app
npm run dev                # Start dev server
npm run build              # Production build
npm run lint               # Lint code

# Backend
python -m uvicorn src.main:app --reload  # Start server
```

## 📦 Package Structure

```
@flowzmith/schema/
├── src/
│   └── index.ts           # TypeScript definitions
├── python/
│   └── schema.py          # Generated Python types
└── scripts/
    └── generate-python.js # Generator script
```

## 🎨 UI Components

| Component | Import |
|-----------|--------|
| Button | `@/components/ui/button` |
| Dialog | `@/components/ui/dialog` |
| Sheet | `@/components/ui/sheet` |
| Input | `@/components/ui/input` |
| Select | `@/components/ui/select` |
| Textarea | `@/components/ui/textarea` |
| Checkbox | `@/components/ui/checkbox` |
| Badge | `@/components/ui/badge` |
| Tabs | `@/components/ui/tabs` |
| ScrollArea | `@/components/ui/scroll-area` |
| Progress | `@/components/ui/progress` |

## 🔌 API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/health` | GET | Health check |
| `/api/contracts/submit` | POST | Create contract |
| `/api/contracts/generate-with-context` | POST | Generate with context |
| `/api/deployments/deploy` | POST | Deploy contract |
| `/api/deployments` | GET | List deployments |
| `/api/documentation/search` | POST | Search docs |
| `/api/flow/init` | POST | Init Flow project |
| `/api/flow/projects` | GET | List projects |
| `/api/system/status` | GET | System status |

## 🎯 Command Categories

| Category | Commands |
|----------|----------|
| **contract** | create_contract, generate_from_context |
| **deployment** | deploy_contract, list_deployments |
| **flow** | flow_init, flow_deploy, flow_list, flow_status, flow_auto |
| **documentation** | search_docs, upload_docs, browse_docs, crawl_docs |
| **system** | setup, status |
| **chat** | chat |

## 🔍 Troubleshooting

| Issue | Solution |
|-------|----------|
| Schema not found | `cd monorepo/packages/flowzmith-schema && npm run build` |
| API connection failed | Check backend is running on port 8000 |
| TypeScript errors | Clear `.next` cache and rebuild |
| Monaco not loading | `npm add @monaco-editor/react` |
| UI components missing | Check Radix UI packages installed |

## 📚 Documentation

| Document | Purpose |
|----------|---------|
| `CENTRALIZED_SCHEMA_ARCHITECTURE.md` | Architecture details |
| `SETUP_CLI_INTEGRATION.md` | Setup instructions |
| `CLI_FRONTEND_INTEGRATION_SUMMARY.md` | Implementation summary |
| `QUICK_REFERENCE.md` | This file |

## 🎨 Icons Available

FileCode, Rocket, Search, Upload, FolderOpen, Globe, History, Activity, Sparkles, FolderPlus, List, Zap, MessageSquare, CheckCircle2, XCircle, Loader2, Terminal, ChevronRight, X

## 🔐 Environment Variables

```env
# Frontend (.env.local)
NEXT_PUBLIC_API_URL=http://localhost:8000

# Backend (.env)
DATABASE_URL=postgresql://...
OPENAI_API_KEY=sk-...
GROQ_API_KEY=gsk_...
```

## 📊 Command Field Types

| Type | Description | Example |
|------|-------------|---------|
| `text` | Single line input | Contract name |
| `textarea` | Multi-line input | Requirements |
| `select` | Dropdown | Network selection |
| `checkbox` | Boolean | Auto-deploy |
| `number` | Numeric input | Limit |
| `file` | File upload | Context files |

## 🎯 Request/Response Types

```typescript
// Request
CreateContractRequest {
  requirements: string
  context?: string
  network: "emulator" | "testnet" | "mainnet"
}

// Response
CreateContractResponse {
  status: "success" | "failed" | "pending"
  submission_id?: string
  generated_contract_code?: string
  error?: string
}
```

## 🚦 Status Values

| Status | Meaning |
|--------|---------|
| `success` | Operation completed |
| `failed` | Operation failed |
| `pending` | In progress |
| `deployed` | Successfully deployed |
| `queued` | Waiting to execute |

## 🎨 Category Colors

| Category | Color |
|----------|-------|
| contract | Blue |
| deployment | Green |
| flow | Purple |
| documentation | Yellow |
| system | Gray |
| chat | Pink |

## 📝 Example Command Definition

```typescript
{
  id: "create_contract",
  name: "Create Contract",
  description: "Create a new smart contract",
  icon: "FileCode",
  category: "contract",
  requiresInput: true,
  steps: [
    {
      id: "requirements",
      title: "Contract Requirements",
      fields: [
        {
          name: "requirements",
          label: "Description",
          type: "textarea",
          required: true,
          placeholder: "Describe your contract..."
        }
      ]
    }
  ]
}
```

## 🔄 Workflow

```
User clicks command
    ↓
Dialog opens
    ↓
User fills form
    ↓
Validation (Zod)
    ↓
API call
    ↓
Backend processes
    ↓
Response returned
    ↓
Results displayed
    ↓
Files shown in editor
```

## 💡 Tips

- Use `Cmd/Ctrl + K` for command palette (if implemented)
- Click category headers to expand/collapse
- Use tabs to switch between editor and history
- Check execution history for past commands
- Monaco editor supports syntax highlighting
- Forms validate in real-time
- Multi-step commands show progress

## 🎓 Learning Path

1. Read `SETUP_CLI_INTEGRATION.md`
2. Review `CENTRALIZED_SCHEMA_ARCHITECTURE.md`
3. Explore schema package code
4. Try adding a simple command
5. Implement backend endpoint
6. Test end-to-end

## 📞 Quick Links

- Frontend: `http://localhost:3000/dashboard/cli`
- Backend: `http://localhost:8000`
- API Docs: `http://localhost:8000/docs`
- Health: `http://localhost:8000/health`

---

**Keep this handy for quick reference!**

# Centralized Schema Architecture

## Overview

This document describes the centralized schema architecture for Flowzmith, which provides a single source of truth for CLI commands, API contracts, and type definitions across the entire codebase.

## Problem Statement

Previously, the CLI commands and API contracts were defined separately in:
1. Python CLI (`cli.py`)
2. FastAPI backend (`src/api/`)
3. Next.js frontend (various components)

This led to:
- **Duplication**: Same types defined multiple times
- **Inconsistency**: Frontend and backend could drift apart
- **Maintenance burden**: Changes required updates in multiple places
- **Type safety issues**: No shared contract between TypeScript and Python

## Solution: @flowzmith/schema Package

We created a centralized schema package that:
1. Defines all CLI commands in one place
2. Provides TypeScript types with Zod validation
3. Auto-generates equivalent Python types
4. Serves as the single source of truth

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                  @flowzmith/schema                          │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  TypeScript Definitions (src/index.ts)               │  │
│  │  - CLI command metadata                              │  │
│  │  - Zod schemas for validation                        │  │
│  │  - TypeScript types                                  │  │
│  └──────────────────────────────────────────────────────┘  │
│                           │                                 │
│                           │ generate-python.js              │
│                           ▼                                 │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Python Definitions (python/schema.py)               │  │
│  │  - TypedDict classes                                 │  │
│  │  - Enum definitions                                  │  │
│  │  - Type hints                                        │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                           │
           ┌───────────────┼───────────────┐
           │               │               │
           ▼               ▼               ▼
    ┌──────────┐    ┌──────────┐   ┌──────────┐
    │ Next.js  │    │ FastAPI  │   │   CLI    │
    │ Frontend │    │ Backend  │   │  (Python)│
    └──────────┘    └──────────┘   └──────────┘
```

## Package Structure

```
monorepo/packages/flowzmith-schema/
├── src/
│   └── index.ts              # Main TypeScript definitions
├── python/
│   └── schema.py             # Auto-generated Python types
├── scripts/
│   └── generate-python.js    # Python type generator
├── package.json
├── tsconfig.json
├── tsup.config.ts
└── README.md
```

## Key Components

### 1. CLI Command Definitions

Each command is defined with:
- **id**: Unique identifier
- **name**: Display name
- **description**: User-facing description
- **icon**: Lucide icon name
- **category**: Grouping (contract, deployment, flow, etc.)
- **requiresInput**: Whether it needs user input
- **steps**: Multi-step form configuration

Example:
```typescript
{
  id: "create_contract",
  name: "Create Contract",
  description: "Create a new smart contract with step-by-step guidance",
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
          label: "Contract Description",
          type: "textarea",
          required: true,
          placeholder: "Describe your smart contract..."
        }
      ]
    }
  ]
}
```

### 2. Request/Response Schemas

Using Zod for runtime validation:

```typescript
export const CreateContractRequestSchema = z.object({
  requirements: z.string().min(1),
  context: z.string().optional(),
  network: z.enum(["emulator", "testnet", "mainnet"]).default("emulator"),
})

export type CreateContractRequest = z.infer<typeof CreateContractRequestSchema>
```

### 3. Python Type Generation

The `generate-python.js` script converts TypeScript types to Python:

```python
class CreateContractRequest(TypedDict, total=False):
    requirements: str
    context: Optional[str]
    network: NetworkType
```

## Frontend Integration

### CLI Sidebar Component

The `CLISidebar` component reads from `CLI_COMMANDS`:

```typescript
import { CLI_COMMANDS, getCommandsByCategory } from "@flowzmith/schema"

export function CLISidebar({ onCommandSelect }) {
  const categories = ["contract", "deployment", "flow", ...]
  
  return (
    <div>
      {categories.map(category => {
        const commands = getCommandsByCategory(category)
        return <CommandList commands={commands} />
      })}
    </div>
  )
}
```

### Command Dialog Component

The `CommandDialog` component renders forms based on command steps:

```typescript
import type { CLICommand } from "@flowzmith/schema"

export function CommandDialog({ command, onExecute }) {
  // Render multi-step form based on command.steps
  // Validate input using Zod schemas
  // Execute command with type-safe data
}
```

### API Client

The API client uses typed requests/responses:

```typescript
import type { CreateContractRequest, CreateContractResponse } from "@flowzmith/schema"

class APIClient {
  async createContract(data: CreateContractRequest): Promise<CreateContractResponse> {
    return this.request("/api/contracts/submit", {
      method: "POST",
      body: JSON.stringify(data),
    })
  }
}
```

## Backend Integration

### FastAPI Endpoints

The backend can import Python types:

```python
from flowzmith_schema import CreateContractRequest, CreateContractResponse

@app.post("/api/contracts/submit")
async def create_contract(request: CreateContractRequest) -> CreateContractResponse:
    # Type-safe request handling
    pass
```

### CLI Tool

The CLI tool uses the same types:

```python
from flowzmith_schema import CLICommandType, CreateContractRequest

def create_contract_interactive():
    request: CreateContractRequest = {
        "requirements": input("Enter requirements: "),
        "network": "emulator"
    }
    # Submit to API
```

## Benefits

### 1. Single Source of Truth
- All commands defined in one place
- No duplication across codebases
- Easy to add/modify commands

### 2. Type Safety
- TypeScript types for frontend
- Python types for backend/CLI
- Runtime validation with Zod
- Compile-time type checking

### 3. Consistency
- Same structure everywhere
- Frontend and backend always in sync
- API contracts enforced

### 4. Developer Experience
- Auto-completion in IDEs
- Clear API documentation
- Easy to understand structure
- Self-documenting code

### 5. Maintainability
- Change once, update everywhere
- Version control for schemas
- Easy to track changes
- Reduced bugs

## Usage Examples

### Adding a New Command

1. **Define in schema package**:

```typescript
// monorepo/packages/flowzmith-schema/src/index.ts

export const MyCommandRequestSchema = z.object({
  param1: z.string(),
  param2: z.number().optional(),
})

export type MyCommandRequest = z.infer<typeof MyCommandRequestSchema>

// Add to CLI_COMMANDS
{
  id: "my_command",
  name: "My Command",
  description: "Does something",
  icon: "Sparkles",
  category: "contract",
  requiresInput: true,
  steps: [...]
}
```

2. **Generate Python types**:

```bash
cd monorepo/packages/flowzmith-schema
npm run generate-python
```

3. **Use in frontend**:

```typescript
import { getCommandById } from "@flowzmith/schema"

const command = getCommandById("my_command")
// Automatically appears in sidebar!
```

4. **Implement in backend**:

```python
from flowzmith_schema import MyCommandRequest

@app.post("/api/my-command")
async def my_command(request: MyCommandRequest):
    # Implementation
    pass
```

### Updating an Existing Command

1. Update the schema in `@flowzmith/schema`
2. Run `npm run generate-python`
3. Frontend and backend automatically get updates
4. TypeScript compiler catches any breaking changes

## File Locations

### Schema Package
- **Location**: `monorepo/packages/flowzmith-schema/`
- **Main file**: `src/index.ts`
- **Generated**: `python/schema.py`

### Frontend Components
- **Sidebar**: `monorepo/apps/app/app/components/cli-sidebar.tsx`
- **Dialog**: `monorepo/apps/app/app/components/command-dialog.tsx`
- **Page**: `monorepo/apps/app/app/app/dashboard/cli/page.tsx`
- **API Client**: `monorepo/apps/app/app/lib/api-client.ts`

### Backend
- **CLI**: `cli.py`
- **API**: `src/api/`
- **Types**: Import from `flowzmith_schema`

## Development Workflow

### 1. Local Development

```bash
# Terminal 1: Watch schema changes
cd monorepo/packages/flowzmith-schema
npm run dev

# Terminal 2: Run frontend
cd monorepo/apps/app/app
npm run dev

# Terminal 3: Run backend
python -m uvicorn src.main:app --reload
```

### 2. Adding Features

1. Define command in schema package
2. Generate Python types
3. Implement backend endpoint
4. Frontend automatically gets the UI
5. Test end-to-end

### 3. Testing

```bash
# Test schema package
cd monorepo/packages/flowzmith-schema
npm run build

# Test frontend integration
cd monorepo/apps/app/app
npm run build

# Test backend integration
python -m pytest
```

## Migration Guide

### From Old CLI to New System

**Before**:
```python
# cli.py
@app.command()
def create_contract():
    # Implementation
```

**After**:
```typescript
// In schema package
{
  id: "create_contract",
  name: "Create Contract",
  // ... metadata
}
```

The CLI command is now:
1. Defined in schema
2. Rendered in frontend UI
3. Executed via API calls
4. Type-safe end-to-end

## Best Practices

1. **Always update schema first**: Make changes in `@flowzmith/schema` before implementing
2. **Run generate-python**: After schema changes, regenerate Python types
3. **Use Zod validation**: Validate all inputs with Zod schemas
4. **Type everything**: Use TypeScript/Python types everywhere
5. **Document changes**: Update this doc when adding major features

## Troubleshooting

### Schema package not found
```bash
cd monorepo/packages/flowzmith-schema
npm install
npm run build
```

### Python types out of sync
```bash
cd monorepo/packages/flowzmith-schema
npm run generate-python
```

### TypeScript errors in frontend
```bash
cd monorepo/apps/app/app
npm install @flowzmith/schema
```

## Future Enhancements

1. **OpenAPI Generation**: Auto-generate OpenAPI specs from schemas
2. **GraphQL Support**: Generate GraphQL types
3. **Validation Middleware**: Automatic request validation
4. **Documentation Site**: Auto-generated API docs
5. **CLI Auto-completion**: Shell completion from schema

## Conclusion

The centralized schema architecture provides:
- ✅ Single source of truth
- ✅ Type safety across languages
- ✅ Consistent API contracts
- ✅ Better developer experience
- ✅ Easier maintenance

All CLI commands are now defined once and work everywhere!

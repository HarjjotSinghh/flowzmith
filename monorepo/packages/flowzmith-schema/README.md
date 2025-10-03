# @flowzmith/schema

Shared schema definitions for Flowzmith CLI and Frontend applications.

## Overview

This package provides a centralized repository for:
- CLI command definitions
- Request/Response type schemas
- Shared TypeScript and Python types
- Command metadata and configuration

## Features

- **Type Safety**: Zod schemas for runtime validation
- **Cross-Platform**: TypeScript types with Python equivalents
- **Single Source of Truth**: One place to define all API contracts
- **Auto-Generation**: Python types generated from TypeScript

## Installation

```bash
# In the monorepo root
npm install

# Or in a specific package
npm install @flowzmith/schema
```

## Usage

### TypeScript/JavaScript

```typescript
import { 
  CLI_COMMANDS, 
  CreateContractRequest,
  CreateContractResponse,
  getCommandById 
} from "@flowzmith/schema"

// Get command metadata
const createCommand = getCommandById("create_contract")

// Validate request data
const requestData: CreateContractRequest = {
  requirements: "Create an NFT contract",
  network: "emulator"
}

// Type-safe response handling
const response: CreateContractResponse = await api.createContract(requestData)
```

### Python

```python
from flowzmith_schema import (
    CLICommandType,
    CreateContractRequest,
    CreateContractResponse
)

# Use typed dictionaries
request: CreateContractRequest = {
    "requirements": "Create an NFT contract",
    "network": "emulator"
}
```

## Development

### Build

```bash
npm run build
```

### Generate Python Types

```bash
npm run generate-python
```

This will create `python/schema.py` with equivalent Python type definitions.

### Watch Mode

```bash
npm run dev
```

## Adding New Commands

1. Add the command type to `CLICommandType` enum
2. Define request/response schemas using Zod
3. Add command metadata to `CLI_COMMANDS` array
4. Run `npm run generate-python` to update Python types

Example:

```typescript
// Add to src/index.ts

export const MyNewCommandRequestSchema = z.object({
  param1: z.string(),
  param2: z.number().optional(),
})

export type MyNewCommandRequest = z.infer<typeof MyNewCommandRequestSchema>

// Add to CLI_COMMANDS
{
  id: "my_new_command",
  name: "My New Command",
  description: "Does something awesome",
  icon: "Sparkles",
  category: "contract",
  requiresInput: true,
  steps: [...]
}
```

## Schema Structure

```
src/
  index.ts          # Main schema definitions
scripts/
  generate-python.js # Python type generator
python/
  schema.py         # Generated Python types
```

## Integration

### Frontend (Next.js)

The frontend imports this package to:
- Render CLI command UI
- Validate form inputs
- Type API requests/responses
- Display command metadata

### Backend (FastAPI)

The backend uses generated Python types to:
- Validate incoming requests
- Type response data
- Ensure API contract compliance

### CLI (Python)

The CLI tool uses Python types for:
- Command definitions
- Request/response handling
- Type hints and validation

## Benefits

1. **No Duplication**: Define types once, use everywhere
2. **Type Safety**: Catch errors at compile time
3. **Documentation**: Self-documenting API contracts
4. **Consistency**: Same structure across all apps
5. **Maintainability**: Single place to update schemas

## License

MIT

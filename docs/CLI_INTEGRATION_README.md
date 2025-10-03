# CLI Frontend Integration - Simplified Approach

## Overview

This implementation uses a **centralized JSON configuration file** that both the Python CLI and the Next.js frontend can read. This approach is simpler, more maintainable, and doesn't require a separate package or complex build processes.

## Architecture

```
flowZmith/
├── config/
│   └── cli-commands.json          # ⭐ Single source of truth
│
├── lib/
│   ├── cli-commands.ts            # TypeScript utilities
│   └── cli_commands.py            # Python utilities
│
├── components/cli/
│   ├── cli-sidebar.tsx            # Command sidebar
│   └── command-dialog.tsx         # Command execution dialog
│
└── app/cli/
    └── page.tsx                   # CLI workspace page
```

## Key Files

### 1. Configuration File (`config/cli-commands.json`)

The single source of truth that defines all CLI commands:

```json
{
  "version": "1.0.0",
  "commands": [
    {
      "id": "create_contract",
      "name": "Create Contract",
      "description": "Create a new smart contract",
      "icon": "FileCode",
      "category": "contract",
      "requiresInput": true,
      "endpoint": "/api/contracts/submit",
      "method": "POST",
      "steps": [...]
    }
  ],
  "categories": [...]
}
```

### 2. TypeScript Utilities (`lib/cli-commands.ts`)

Functions to read and use the configuration in the frontend:

```typescript
import { getAllCommands, getCommandById } from '@/lib/cli-commands'

const commands = getAllCommands()
const command = getCommandById('create_contract')
```

### 3. Python Utilities (`lib/cli_commands.py`)

Functions to read and use the configuration in the CLI:

```python
from lib.cli_commands import get_all_commands, get_command_by_id

commands = get_all_commands()
command = get_command_by_id('create_contract')
```

## Benefits

### ✅ Simple
- Single JSON file
- No build process
- No package management
- Easy to understand

### ✅ Maintainable
- One place to update
- Version controlled
- Clear structure
- Self-documenting

### ✅ Flexible
- Easy to add commands
- Easy to modify
- No code changes needed
- Just update JSON

### ✅ Cross-Platform
- Works in TypeScript
- Works in Python
- Same data structure
- Consistent behavior

## Usage

### Adding a New Command

1. **Edit `config/cli-commands.json`**:

```json
{
  "id": "my_new_command",
  "name": "My New Command",
  "description": "Does something awesome",
  "icon": "Sparkles",
  "category": "contract",
  "requiresInput": true,
  "endpoint": "/api/my-command",
  "method": "POST",
  "steps": [
    {
      "id": "input",
      "title": "Input Parameters",
      "fields": [
        {
          "name": "param1",
          "label": "Parameter 1",
          "type": "text",
          "required": true
        }
      ]
    }
  ]
}
```

2. **That's it!** The command will automatically appear in:
   - Frontend sidebar
   - CLI command list
   - Both will use the same configuration

### Frontend Usage

```typescript
// In your component
import { getAllCommands } from '@/lib/cli-commands'

const commands = getAllCommands()
// Render commands in UI
```

### Python CLI Usage

```python
# In your CLI
from lib.cli_commands import get_all_commands

commands = get_all_commands()
# Use commands in CLI
```

## File Locations

### Frontend (Next.js)
- **Config**: `flowZmith/config/cli-commands.json`
- **Utils**: `flowZmith/lib/cli-commands.ts`
- **Components**: `flowZmith/components/cli/`
- **Page**: `flowZmith/app/cli/page.tsx`

### Backend (Python)
- **Config**: `flowZmith/config/cli-commands.json` (same file!)
- **Utils**: `flowZmith/lib/cli_commands.py`
- **CLI**: `cli.py`

## Command Structure

### Minimal Command

```json
{
  "id": "simple_command",
  "name": "Simple Command",
  "description": "A simple command",
  "icon": "Zap",
  "category": "system",
  "requiresInput": false
}
```

### Command with Form

```json
{
  "id": "form_command",
  "name": "Form Command",
  "description": "Command with input form",
  "icon": "FileCode",
  "category": "contract",
  "requiresInput": true,
  "endpoint": "/api/endpoint",
  "method": "POST",
  "steps": [
    {
      "id": "step1",
      "title": "Step 1",
      "fields": [
        {
          "name": "field1",
          "label": "Field 1",
          "type": "text",
          "required": true,
          "placeholder": "Enter value..."
        }
      ]
    }
  ]
}
```

### Command with Redirect

```json
{
  "id": "chat",
  "name": "Chat",
  "description": "Open chat interface",
  "icon": "MessageSquare",
  "category": "chat",
  "requiresInput": false,
  "redirectTo": "/chat"
}
```

## Field Types

Supported field types:
- `text` - Single line text input
- `textarea` - Multi-line text input
- `select` - Dropdown selection
- `checkbox` - Boolean checkbox
- `number` - Numeric input
- `file` - File upload (future)

## Categories

Available categories:
- `contract` - Smart contract operations
- `deployment` - Deployment operations
- `flow` - Flow CLI operations
- `documentation` - Documentation operations
- `system` - System operations
- `chat` - Chat interface

## Quick Start

### 1. Access the CLI Interface

```bash
# Start your Next.js app
cd flowZmith
npm run dev

# Visit
open http://localhost:3000/cli
```

### 2. Use the Python CLI

```bash
# The CLI automatically reads the same config
python cli.py --help
```

### 3. Add a Command

Edit `config/cli-commands.json` and add your command. It will appear in both interfaces immediately!

## Migration from Old Approach

If you were using the monorepo package approach:

1. ✅ Delete `monorepo/packages/flowzmith-schema/`
2. ✅ Use `flowZmith/config/cli-commands.json` instead
3. ✅ Import from `@/lib/cli-commands` in frontend
4. ✅ Import from `lib.cli_commands` in Python

## Troubleshooting

### Command not appearing?

1. Check JSON syntax in `config/cli-commands.json`
2. Restart dev server
3. Clear browser cache

### TypeScript errors?

1. Check import path: `@/lib/cli-commands`
2. Ensure `tsconfig.json` has correct paths
3. Restart TypeScript server

### Python errors?

1. Check import: `from lib.cli_commands import ...`
2. Ensure `config/cli-commands.json` exists
3. Check file permissions

## Best Practices

1. **Always validate JSON** - Use a JSON validator
2. **Use meaningful IDs** - Use snake_case for command IDs
3. **Add descriptions** - Help users understand commands
4. **Test both sides** - Test in frontend and CLI
5. **Version your config** - Update version number when changing

## Future Enhancements

- [ ] JSON Schema validation
- [ ] Command aliases
- [ ] Command groups
- [ ] Conditional fields
- [ ] Field validation rules
- [ ] Command dependencies

## Summary

This approach provides:
- ✅ Single source of truth (JSON file)
- ✅ Works in TypeScript and Python
- ✅ No build process required
- ✅ Easy to maintain and extend
- ✅ Version controlled
- ✅ Self-documenting

**Much simpler than the package approach!**

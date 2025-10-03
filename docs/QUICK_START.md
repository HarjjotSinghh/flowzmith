# Quick Start Guide

## 🚀 Get Started in 5 Minutes

### Step 1: Access the CLI Interface (1 minute)

```bash
cd flowZmith
npm run dev
```

Then visit: **http://localhost:3000/cli**

### Step 2: Try a Command (2 minutes)

1. Click **"Create Contract"** in the sidebar
2. Fill in the requirements
3. Select network (emulator/testnet/mainnet)
4. Click **"Execute"**
5. View the generated contract in the editor!

### Step 3: Add Your Own Command (2 minutes)

Edit `flowZmith/config/cli-commands.json`:

```json
{
  "id": "my_command",
  "name": "My Command",
  "description": "My awesome command",
  "icon": "Sparkles",
  "category": "contract",
  "requiresInput": true,
  "endpoint": "/api/my-endpoint",
  "method": "POST",
  "steps": [
    {
      "id": "input",
      "title": "Input",
      "fields": [
        {
          "name": "text",
          "label": "Enter Text",
          "type": "text",
          "required": true
        }
      ]
    }
  ]
}
```

Refresh the page - your command appears!

## 📚 Learn More

- **Full Guide**: [CLI_INTEGRATION_README.md](./CLI_INTEGRATION_README.md)
- **Migration**: [MIGRATION_GUIDE.md](./MIGRATION_GUIDE.md)
- **Summary**: [FINAL_IMPLEMENTATION_SUMMARY.md](./FINAL_IMPLEMENTATION_SUMMARY.md)

## 🎯 Key Files

| File | Purpose |
|------|---------|
| `config/cli-commands.json` | Command definitions |
| `lib/cli-commands.ts` | TypeScript utilities |
| `lib/cli_commands.py` | Python utilities |
| `components/cli/cli-sidebar.tsx` | Sidebar component |
| `components/cli/command-dialog.tsx` | Dialog component |
| `app/cli/page.tsx` | Main page |

## ✅ That's It!

You now have a working CLI frontend integration. It's that simple!

**Next**: Read [CLI_INTEGRATION_README.md](./CLI_INTEGRATION_README.md) for details.

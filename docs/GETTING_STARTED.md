# Getting Started with CLI Frontend Integration

Welcome! This guide will get you up and running with the Flowzmith CLI frontend integration in under 10 minutes.

## 🎯 What You're Building

Transform this:
```bash
$ python cli.py create-contract
```

Into this:
```
Beautiful web interface with visual command selection,
multi-step wizards, code editor, and execution history
```

## 📋 Prerequisites

Before starting, ensure you have:

- ✅ Node.js >= 18
- ✅ npm, yarn, or bun
- ✅ Python >= 3.8
- ✅ FastAPI backend running
- ✅ 10 minutes of time

## 🚀 Quick Start (3 Steps)

### Step 1: Build Schema Package (2 minutes)

```bash
cd monorepo/packages/flowzmith-schema
npm install
npm run build
npm run generate-python
```

**What this does**: Creates the centralized schema that both frontend and backend use.

### Step 2: Install Frontend Dependencies (2 minutes)

```bash
cd ../../apps/app/app
npm install
```

**What this does**: Installs all required packages including Monaco editor and UI components.

### Step 3: Start Development Server (1 minute)

```bash
npm run dev
```

**What this does**: Starts the Next.js development server.

### Step 4: Open in Browser (30 seconds)

```bash
open http://localhost:3000/dashboard/cli
```

**What you'll see**: A beautiful interface with all your CLI commands!

## ✅ Verify It Works

You should see:
1. ✅ Sidebar with command categories
2. ✅ Commands organized by type
3. ✅ Click a command → dialog opens
4. ✅ Fill form → execute → see results

## 🎓 Next Steps

### Learn the Basics (5 minutes)

1. **Click "Create Contract"**
   - See the multi-step wizard
   - Fill in requirements
   - Select network
   - Execute and view results

2. **Click "System Status"**
   - See instant execution
   - View system statistics

3. **Check Execution History**
   - Switch to History tab
   - See past commands

### Explore the Code (10 minutes)

1. **Schema Package**
   ```bash
   cat monorepo/packages/flowzmith-schema/src/index.ts
   ```
   See how commands are defined

2. **CLI Sidebar**
   ```bash
   cat monorepo/apps/app/app/components/cli-sidebar.tsx
   ```
   See how commands are rendered

3. **Command Dialog**
   ```bash
   cat monorepo/apps/app/app/components/command-dialog.tsx
   ```
   See how forms are generated

### Add Your First Command (15 minutes)

Follow the guide in [SETUP_CLI_INTEGRATION.md](./SETUP_CLI_INTEGRATION.md#adding-new-commands)

## 📚 Documentation Overview

| Document | When to Read | Time |
|----------|--------------|------|
| **GETTING_STARTED.md** | Right now! | 5 min |
| **README_CLI_INTEGRATION.md** | Overview and features | 10 min |
| **QUICK_REFERENCE.md** | Quick lookups | 2 min |
| **SETUP_CLI_INTEGRATION.md** | Detailed setup | 20 min |
| **CENTRALIZED_SCHEMA_ARCHITECTURE.md** | Deep dive | 30 min |
| **CLI_FRONTEND_INTEGRATION_SUMMARY.md** | Implementation details | 15 min |
| **IMPLEMENTATION_CHECKLIST.md** | Verification | 10 min |

## 🎯 Recommended Reading Order

### Day 1: Get It Running (30 minutes)
1. ✅ GETTING_STARTED.md (this file)
2. ✅ README_CLI_INTEGRATION.md
3. ✅ QUICK_REFERENCE.md
4. ✅ Try the interface

### Day 2: Understand It (1 hour)
1. ✅ SETUP_CLI_INTEGRATION.md
2. ✅ CENTRALIZED_SCHEMA_ARCHITECTURE.md
3. ✅ Add a simple command

### Day 3: Master It (2 hours)
1. ✅ CLI_FRONTEND_INTEGRATION_SUMMARY.md
2. ✅ IMPLEMENTATION_CHECKLIST.md
3. ✅ Customize for your needs

## 🔧 Common Issues

### Issue: Schema package not found

**Solution**:
```bash
cd monorepo/packages/flowzmith-schema
npm install && npm run build
```

### Issue: API connection failed

**Solution**:
```bash
# Check backend is running
curl http://localhost:8000/health

# If not, start it
python -m uvicorn src.main:app --reload
```

### Issue: TypeScript errors

**Solution**:
```bash
# Clear cache
rm -rf .next
npm run dev
```

### Issue: Monaco editor not loading

**Solution**:
```bash
npm install @monaco-editor/react
```

## 🎨 What Each File Does

### Schema Package
```
monorepo/packages/flowzmith-schema/
├── src/index.ts              # Command definitions
├── python/schema.py          # Generated Python types
└── scripts/generate-python.js # Type generator
```

### Frontend Components
```
monorepo/apps/app/app/
├── components/
│   ├── cli-sidebar.tsx       # Command browser
│   ├── command-dialog.tsx    # Form wizard
│   └── ui/                   # UI components
├── app/dashboard/cli/
│   └── page.tsx              # Main workspace
└── lib/
    └── api-client.ts         # API calls
```

## 🎯 Key Concepts

### 1. Single Source of Truth
All commands defined once in `@flowzmith/schema`

### 2. Type Safety
TypeScript + Python types ensure consistency

### 3. Auto-Generation
Python types generated from TypeScript

### 4. Visual Interface
CLI commands → Beautiful web UI

## 💡 Pro Tips

1. **Use Watch Mode**
   ```bash
   # Terminal 1
   cd monorepo/packages/flowzmith-schema
   npm run dev
   
   # Terminal 2
   cd monorepo/apps/app/app
   npm run dev
   ```

2. **Check the Quick Reference**
   Keep [QUICK_REFERENCE.md](./QUICK_REFERENCE.md) handy

3. **Use the Checklist**
   Follow [IMPLEMENTATION_CHECKLIST.md](./IMPLEMENTATION_CHECKLIST.md)

4. **Read Error Messages**
   They're usually helpful!

## 🎓 Learning Path

```
Start Here
    ↓
Quick Start (10 min)
    ↓
Try the Interface (10 min)
    ↓
Read Documentation (1 hour)
    ↓
Add a Command (30 min)
    ↓
Customize (2 hours)
    ↓
Master It! 🎉
```

## 📞 Need Help?

1. **Check Documentation**
   - All guides are in the root directory
   - Start with README_CLI_INTEGRATION.md

2. **Review Examples**
   - Look at existing commands in schema
   - Check how they're implemented

3. **Check Logs**
   - Frontend: Browser console
   - Backend: `tail -f server.log`

4. **Verify Setup**
   - Use IMPLEMENTATION_CHECKLIST.md
   - Ensure all steps are complete

## 🎉 Success Indicators

You'll know it's working when:

1. ✅ `/dashboard/cli` loads without errors
2. ✅ Sidebar shows all commands
3. ✅ Clicking a command opens dialog
4. ✅ Executing a command shows results
5. ✅ Editor displays generated files
6. ✅ History tracks executions

## 🚀 What's Next?

After getting it running:

1. **Explore All Commands**
   - Try each category
   - See different form types
   - Check various outputs

2. **Add a Custom Command**
   - Follow the 3-step guide
   - See it appear automatically
   - Test end-to-end

3. **Customize the UI**
   - Modify colors
   - Add features
   - Enhance UX

4. **Deploy to Production**
   - Build for production
   - Configure environment
   - Deploy!

## 📊 Time Investment

| Activity | Time | Value |
|----------|------|-------|
| Quick Start | 10 min | Get it running |
| Try Interface | 10 min | See it work |
| Read Docs | 1 hour | Understand it |
| Add Command | 30 min | Customize it |
| **Total** | **2 hours** | **Full mastery** |

## 🎯 Goals

By the end of this guide, you will:

- ✅ Have a working CLI frontend
- ✅ Understand the architecture
- ✅ Know how to add commands
- ✅ Be able to customize it
- ✅ Have production-ready code

## 🎊 Congratulations!

You're now ready to use the CLI frontend integration!

### Quick Links

- 🌐 Frontend: http://localhost:3000/dashboard/cli
- 🔧 Backend: http://localhost:8000
- 📚 API Docs: http://localhost:8000/docs
- ❤️ Health: http://localhost:8000/health

### Next Steps

1. ✅ Complete the Quick Start above
2. ✅ Read README_CLI_INTEGRATION.md
3. ✅ Try adding a command
4. ✅ Explore the documentation
5. ✅ Build something awesome!

---

**Happy coding! 🚀**

*Questions? Check the documentation or review the troubleshooting section.*

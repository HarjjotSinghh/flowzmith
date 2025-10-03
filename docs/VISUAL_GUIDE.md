# Visual Guide - CLI Workspace with Terminal

## 🖥️ Complete Interface Layout

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                                                                                 │
│  ┌─────────────────┐  ┌──────────────────────────────────────────────────────┐ │
│  │                 │  │  CLI Workspace                                        │ │
│  │  Flowzmith CLI  │  │  Execute CLI commands and view results in real-time  │ │
│  │                 │  └──────────────────────────────────────────────────────┘ │
│  │  Smart Contracts│  ┌──────────────┬──────────────────────────────────────┐ │
│  │  • Create       │  │              │                                      │ │
│  │  • Generate     │  │  Generated   │  [Editor] [Terminal] [History]      │ │
│  │                 │  │  Files       │                                      │ │
│  │  Deployment     │  │              │  ┌────────────────────────────────┐ │ │
│  │  • Deploy       │  │  Contract.cdc│  │ 🖥️ Terminal Output  ● Streaming│ │ │
│  │  • List         │  │  flow.json   │  │        [Auto-scroll: ON] [X]   │ │ │
│  │                 │  │              │  ├────────────────────────────────┤ │ │
│  │  Flow CLI       │  │              │  │ 12:34:56.789 ▶ Executing...   │ │ │
│  │  • Init         │  │              │  │ 12:34:56.790 ℹ️ Calling API... │ │ │
│  │  • Deploy       │  │              │  │ 12:34:57.123 ℹ️ Receiving...   │ │ │
│  │  • List         │  │              │  │ 12:34:58.456 ✅ Completed      │ │ │
│  │                 │  │              │  │                                │ │ │
│  │  Documentation  │  │              │  │                                │ │ │
│  │  • Search       │  │              │  │                                │ │ │
│  │  • Upload       │  │              │  ├────────────────────────────────┤ │ │
│  │                 │  │              │  │ 4 lines      Receiving data... │ │ │
│  │  System         │  │              │  └────────────────────────────────┘ │ │
│  │  • Status       │  │              │                                      │ │
│  │                 │  │              │                                      │ │
│  └─────────────────┘  └──────────────┴──────────────────────────────────────┘ │
│                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
```

## 📊 Terminal Output Detail

```
┌─────────────────────────────────────────────────────────────┐
│ 🖥️ Terminal Output                    ● Streaming...       │
│                          [Auto-scroll: ON] [X]              │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ 12:34:56.789  ▶  Executing command: Generate from Context  │
│ 12:34:56.790  ℹ️  Parameters: {                             │
│                    "requirements": "Create NFT contract",   │
│                    "network": "emulator"                    │
│                  }                                          │
│ 12:34:56.791  ℹ️  Calling API endpoint: POST /api/...      │
│ 12:34:56.792  ℹ️  Receiving streaming response...          │
│ 12:34:57.123  ℹ️  Reading context files...                 │
│ 12:34:57.456  ℹ️  Analyzing requirements...                │
│ 12:34:58.123  ℹ️  Generating contract structure...         │
│ 12:34:59.456  ℹ️  Adding contract logic...                 │
│ 12:35:00.789  ℹ️  Validating contract...                   │
│ 12:35:01.123  ✅  Contract generation completed            │
│ 12:35:01.124  ✅  Generated contract code received         │
│ 12:35:01.125  ℹ️  Contract name: NFTContract               │
│ 12:35:01.126  ✅  Files added to workspace                 │
│ 12:35:01.127  ✅  Command completed successfully           │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│ 17 lines                            Receiving data...       │
└─────────────────────────────────────────────────────────────┘
```

## 🎨 Color Scheme

### Terminal Colors
```
Background:  ███████  Black (#000000)
Header:      ███████  Dark Gray (#1a1a1a)
Text:        ███████  Light Gray (#d4d4d4)
Timestamp:   ███████  Muted Gray (#737373)

Log Types:
Info:        ███████  Gray (#d4d4d4)
Success:     ███████  Green (#4ade80)
Error:       ███████  Red (#f87171)
Warning:     ███████  Yellow (#fbbf24)
Command:     ███████  Blue (#60a5fa)
```

## 🔄 Execution Flow Visualization

```
┌─────────────┐
│ User clicks │
│   command   │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   Dialog    │
│   opens     │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ User fills  │
│    form     │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   Execute   │
│   clicked   │
└──────┬──────┘
       │
       ▼
┌─────────────────────────────────────┐
│ Terminal Tab                        │
│                                     │
│ 12:34:56.789 ▶ Executing command... │ ← Command starts
│ 12:34:56.790 ℹ️ Calling API...      │ ← API call
│ 12:34:56.791 ℹ️ Receiving...        │ ← Streaming starts
│ 12:34:57.123 ℹ️ Processing...       │ ← Real-time updates
│ 12:34:58.456 ✅ Completed           │ ← Success
└─────────────────────────────────────┘
       │
       ▼
┌─────────────┐
│   Files     │
│  generated  │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   Editor    │
│   updated   │
└─────────────┘
```

## 📱 Tab States

### Editor Tab (Default)
```
┌────────────────────────────────────────┐
│ [Editor] Terminal History              │
├────────────────────────────────────────┤
│                                        │
│  // Contract.cdc                       │
│  access(all) contract NFTContract {    │
│      ...                               │
│  }                                     │
│                                        │
└────────────────────────────────────────┘
```

### Terminal Tab (Active)
```
┌────────────────────────────────────────┐
│ Editor [Terminal] History              │
├────────────────────────────────────────┤
│ 🖥️ Terminal Output    ● Streaming...   │
│                  [Auto-scroll: ON] [X] │
├────────────────────────────────────────┤
│ 12:34:56.789 ▶ Executing...           │
│ 12:34:56.790 ℹ️ Processing...          │
│ 12:34:57.123 ✅ Completed              │
└────────────────────────────────────────┘
```

### History Tab
```
┌────────────────────────────────────────┐
│ Editor Terminal [History]              │
├────────────────────────────────────────┤
│ ┌────────────────────────────────────┐ │
│ │ Create Contract          [success] │ │
│ │ 2024-01-15 12:34:56               │ │
│ │ Project: /path/to/project         │ │
│ └────────────────────────────────────┘ │
└────────────────────────────────────────┘
```

## 🎯 Interactive Elements

### Sidebar Command
```
┌─────────────────────────────────┐
│ Smart Contracts            [3]  │  ← Category header
│   ▼                             │  ← Expand/collapse
│                                 │
│   ┌───────────────────────────┐ │
│   │ 📄 Create Contract        │ │  ← Command button
│   │ Create a new smart        │ │
│   │ contract with guidance    │ │
│   └───────────────────────────┘ │
│                                 │
└─────────────────────────────────┘
```

### Terminal Controls
```
┌─────────────────────────────────────────┐
│ 🖥️ Terminal Output    ● Streaming...    │
│                  [Auto-scroll: ON] [X]  │  ← Controls
│                       ↑           ↑     │
│                       │           │     │
│                  Toggle auto   Clear    │
│                    scroll      logs     │
└─────────────────────────────────────────┘
```

## 🔔 Status Indicators

### Streaming Active
```
● Streaming...  ← Green pulsing dot
```

### Auto-scroll ON
```
[Auto-scroll: ON]  ← Button highlighted
```

### Auto-scroll OFF
```
[Auto-scroll: OFF]  ← Button normal
```

### Line Count
```
17 lines  ← Bottom left
```

### Streaming Status
```
Receiving data...  ← Bottom right
```

## 📊 Log Entry Anatomy

```
┌─────────────┬───┬──────────────────────────────────┐
│ Timestamp   │ ● │ Message                          │
└─────────────┴───┴──────────────────────────────────┘
  12:34:56.789  ℹ️  Calling API endpoint: POST /api/...
  ↑             ↑   ↑
  │             │   └─ Message text (color-coded)
  │             └───── Emoji indicator
  └─────────────────── Millisecond precision timestamp
```

## 🎨 Hover Effects

### Command Button (Hover)
```
┌───────────────────────────┐
│ 📄 Create Contract        │  ← Background changes
│ Create a new smart        │
│ contract with guidance    │
└───────────────────────────┘
```

### Log Entry (Hover)
```
12:34:56.789 ℹ️ Processing...  ← Background highlight
```

## 🚀 Complete User Journey

```
1. User opens /cli
   ↓
2. Sees sidebar with commands
   ↓
3. Clicks "Generate from Context"
   ↓
4. Dialog opens with form
   ↓
5. Fills requirements
   ↓
6. Clicks "Execute"
   ↓
7. Terminal tab activates automatically
   ↓
8. Sees real-time logs streaming
   ↓
9. Command completes
   ↓
10. Switches to Editor tab
    ↓
11. Views generated contract
    ↓
12. Switches to History tab
    ↓
13. Reviews execution history
```

## 💡 Tips for Best Experience

1. **Keep Terminal tab open** during execution
2. **Enable auto-scroll** for real-time monitoring
3. **Disable auto-scroll** to review specific logs
4. **Clear logs** before new commands for clarity
5. **Watch timestamps** to identify slow operations

---

**Visual guide complete!** 🎨

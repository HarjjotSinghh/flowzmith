# CLI Workspace UI Guide

## Interface Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  CLI Workspace                                                              │
│  Execute CLI commands and view results in real-time                         │
├──────────────┬──────────────────────────────────────────────────────────────┤
│              │                                                               │
│  Flowzmith   │  ┌─────────────────────────────────────────────────────────┐│
│  CLI         │  │  Generated Files                                        ││
│              │  ├─────────────────────────────────────────────────────────┤│
│  ┌─────────┐│  │  ▼ contracts/                                           ││
│  │Contract │││  │    └─ UserProfile.cdc                                   ││
│  ├─────────┤││  │  ▼ transactions/                                        ││
│  │Create   │││  │    ├─ deploy_contract.cdc                               ││
│  │Deploy   │││  │    └─ interact_contract.cdc                             ││
│  │Test     │││  │  ▼ scripts/                                             ││
│  └─────────┘││  │    ├─ read_contract_data.cdc                            ││
│              │  │    └─ check_contract_status.cdc                          ││
│  ┌─────────┐│  │  ▼ tests/                                                ││
│  │Flow     │││  │    └─ test_deployment.cdc                               ││
│  ├─────────┤││  │  ▶ flow.json                                            ││
│  │Projects │││  │  ▶ README.md                                            ││
│  │Deploy   │││  │  ▶ metadata.json                                        ││
│  └─────────┘││  └─────────────────────────────────────────────────────────┘│
│              │                                                               │
│              │  ┌─────────────────────────────────────────────────────────┐│
│              │  │ [Export ▼] [Push to GitHub] | [Compile] [Deploy]       ││
│              │  ├─────────────────────────────────────────────────────────┤│
│              │  │                                                          ││
│              │  │  pub contract UserProfile {                             ││
│              │  │                                                          ││
│              │  │      pub var profiles: {Address: Profile}               ││
│              │  │                                                          ││
│              │  │      pub struct Profile {                               ││
│              │  │          pub let name: String                           ││
│              │  │          pub let bio: String                            ││
│              │  │          pub let avatar: String                         ││
│              │  │                                                          ││
│              │  │          init(name: String, bio: String, avatar: String)││
│              │  │              self.name = name                           ││
│              │  │              self.bio = bio                             ││
│              │  │              self.avatar = avatar                       ││
│              │  │          }                                              ││
│              │  │      }                                                  ││
│              │  │                                                          ││
│              │  │      init() {                                           ││
│              │  │          self.profiles = {}                            ││
│              │  │      }                                                  ││
│              │  │  }                                                      ││
│              │  │                                                          ││
│              │  └─────────────────────────────────────────────────────────┘│
│              │                                                               │
│              │  [Editor] [Terminal ●] [History]                             │
│              │                                                               │
└──────────────┴──────────────────────────────────────────────────────────────┘
```

## Component Breakdown

### 1. Sidebar (Left)

```
┌─────────────────┐
│  Flowzmith CLI  │
│                 │
│  ▼ Contract     │
│    • Create     │
│    • Deploy     │
│    • Test       │
│                 │
│  ▼ Flow         │
│    • Projects   │
│    • Deploy     │
│    • Status     │
│                 │
│  ▼ System       │
│    • Setup      │
│    • Health     │
│                 │
│  Version: 1.0.0 │
│  Commands: 12   │
└─────────────────┘
```

**Features:**
- Collapsible categories
- Command count badges
- Version information
- Hover effects
- Active command highlighting

### 2. File Explorer (Left-Center)

```
┌─────────────────────────┐
│  Generated Files        │
├─────────────────────────┤
│  ▼ 📁 contracts         │
│    └─ 📄 Contract.cdc   │ ← Selected
│  ▼ 📁 transactions      │
│    ├─ 📄 deploy.cdc     │
│    └─ 📄 interact.cdc   │
│  ▶ 📁 scripts           │
│  ▶ 📁 tests             │
│  📄 flow.json           │
│  📄 README.md           │
└─────────────────────────┘
```

**Features:**
- Folder expansion/collapse
- File type icons
- Selection highlighting
- Nested indentation
- Smooth animations

### 3. Action Toolbar (Top of Editor)

```
┌────────────────────────────────────────────────────────────┐
│  [Export ▼] [Push to GitHub]  |  [Compile] [Deploy]       │
└────────────────────────────────────────────────────────────┘
```

**Export Dropdown:**
```
┌─────────────────┐
│ Export as .zip  │
│ Export as .tar  │
└─────────────────┘
```

**Button States:**
- Normal: White background
- Hover: Light gray background
- Loading: Spinner icon + disabled
- Disabled: Gray text + no hover

### 4. Monaco Editor (Center)

```
┌─────────────────────────────────────────────────────────────┐
│  1  pub contract UserProfile {                              │
│  2                                                           │
│  3      pub var profiles: {Address: Profile}                │
│  4                                                           │
│  5      pub struct Profile {                                │
│  6          pub let name: String                            │
│  7          pub let bio: String                             │
│  8          pub let avatar: String                          │
│  9                                                           │
│ 10          init(name: String, bio: String, avatar: String) │
│ 11              self.name = name                            │
│ 12              self.bio = bio                              │
│ 13              self.avatar = avatar                        │
│ 14          }                                               │
│ 15      }                                                   │
│ 16                                                           │
│ 17      init() {                                            │
│ 18          self.profiles = {}                             │
│ 19      }                                                   │
│ 20  }                                                       │
└─────────────────────────────────────────────────────────────┘
```

**Features:**
- Line numbers
- Syntax highlighting
- Dark theme
- Auto-completion
- Code folding
- Find/replace (Ctrl+F)
- Multi-cursor editing

### 5. Tabs (Below Editor)

```
┌──────────────────────────────────────┐
│  [Editor] [Terminal ●] [History]     │
└──────────────────────────────────────┘
```

**Active Indicators:**
- Underline for active tab
- Green dot (●) when streaming
- Badge count for history items

### 6. Terminal Tab

```
┌─────────────────────────────────────────────────────────────┐
│  Terminal Output                              [Clear] [Auto]│
├─────────────────────────────────────────────────────────────┤
│  $ Executing command: Create Contract                       │
│  ℹ Parameters: { "contract_name": "UserProfile" }          │
│  ℹ Calling API endpoint: POST /api/contracts/submit        │
│  ℹ Transformed request data: { ... }                       │
│  ✓ Response received                                        │
│  ℹ Loading project files...                                │
│  ✓ Loaded 9 files                                          │
│  ✓ Command "Create Contract" completed successfully        │
│                                                              │
│  $ Compiling UserProfile.cdc...                            │
│  ✓ Compilation successful!                                 │
│                                                              │
│  $ Deploying UserProfile.cdc on-chain...                   │
│  ✓ Deployment successful!                                  │
│  ℹ Transaction ID: 0x1234567890abcdef                      │
│  ℹ Contract Address: 0xabcdef1234567890                    │
└─────────────────────────────────────────────────────────────┘
```

**Log Types:**
- `$` Command (blue)
- `ℹ` Info (gray)
- `✓` Success (green)
- `⚠` Warning (yellow)
- `✗` Error (red)

### 7. History Tab

```
┌─────────────────────────────────────────────────────────────┐
│  Execution History                                          │
├─────────────────────────────────────────────────────────────┤
│  ┌───────────────────────────────────────────────────────┐ │
│  │  Create Contract                        [success]     │ │
│  │  Oct 3, 2025, 10:46:35 PM                            │ │
│  │  Project: flow_projects/abc123                       │ │
│  └───────────────────────────────────────────────────────┘ │
│                                                              │
│  ┌───────────────────────────────────────────────────────┐ │
│  │  Deploy Contract                        [deployed]    │ │
│  │  Oct 3, 2025, 10:47:12 PM                            │ │
│  │  Transaction: 0x1234...                              │ │
│  └───────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

**Features:**
- Chronological order (newest first)
- Status badges
- Expandable details
- Timestamp display

### 8. Command Dialog

```
┌─────────────────────────────────────────────────────────────┐
│  Create Contract                                        [×] │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Generate a new Flow smart contract                         │
│                                                              │
│  Contract Name *                                            │
│  ┌────────────────────────────────────────────────────────┐│
│  │ UserProfile                                            ││
│  └────────────────────────────────────────────────────────┘│
│                                                              │
│  Description                                                │
│  ┌────────────────────────────────────────────────────────┐│
│  │ A smart contract for creating and managing user        ││
│  │ profiles.                                              ││
│  └────────────────────────────────────────────────────────┘│
│                                                              │
│  Network                                                    │
│  ┌────────────────────────────────────────────────────────┐│
│  │ Testnet                                        ▼       ││
│  └────────────────────────────────────────────────────────┘│
│                                                              │
│  Features                                                   │
│  ☑ Include transactions                                    │
│  ☑ Include deployment scripts                              │
│  ☑ Include test cases                                      │
│                                                              │
│                                    [Cancel]  [Execute]      │
└─────────────────────────────────────────────────────────────┘
```

**Features:**
- Multi-step wizard (if needed)
- Progress indicator
- Field validation
- Help text
- Required field markers (*)

### 9. Loading Overlay

```
┌─────────────────────────────────────────────────────────────┐
│                                                              │
│                                                              │
│                         ⟳                                   │
│                                                              │
│                    Processing...                            │
│                                                              │
│         Generating contract files and setting up            │
│                  project structure                          │
│                                                              │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

**Features:**
- Semi-transparent backdrop
- Centered modal
- Spinning loader
- Status message
- Prevents interaction

## Color Scheme

### Light Mode (Default)
- Background: `#ffffff`
- Text: `#000000`
- Border: `#e5e7eb`
- Accent: `#3b82f6`
- Success: `#10b981`
- Warning: `#f59e0b`
- Error: `#ef4444`

### Dark Mode (Editor)
- Background: `#1e1e1e`
- Text: `#d4d4d4`
- Border: `#3e3e42`
- Accent: `#569cd6`
- Success: `#4ec9b0`
- Warning: `#dcdcaa`
- Error: `#f48771`

## Responsive Behavior

### Desktop (1920px+)
```
[Sidebar 256px] [File Tree 256px] [Editor Flex] [Terminal]
```

### Laptop (1280px)
```
[Sidebar 200px] [File Tree 200px] [Editor Flex] [Terminal]
```

### Tablet (768px)
```
[Sidebar Collapsed] [File Tree 200px] [Editor Flex]
[Terminal Below]
```

### Mobile (< 768px)
```
[Hamburger Menu]
[Editor Full Width]
[Terminal Below]
```

## Keyboard Shortcuts

### Editor
- `Ctrl+S` / `Cmd+S` - Save (auto-save enabled)
- `Ctrl+F` / `Cmd+F` - Find
- `Ctrl+H` / `Cmd+H` - Replace
- `Ctrl+/` / `Cmd+/` - Toggle comment
- `Ctrl+D` / `Cmd+D` - Select next occurrence
- `Alt+Up/Down` - Move line up/down

### Navigation
- `Ctrl+B` / `Cmd+B` - Toggle sidebar
- `Ctrl+\` / `Cmd+\` - Toggle file tree
- `Ctrl+~` / `Cmd+~` - Toggle terminal

## Accessibility

### Screen Reader Support
- ARIA labels on all buttons
- Semantic HTML structure
- Keyboard navigation
- Focus indicators

### Keyboard Navigation
- Tab through all interactive elements
- Enter to activate buttons
- Arrow keys in file tree
- Escape to close dialogs

## Animation Timing

- Folder expand/collapse: 200ms
- Button hover: 150ms
- Tab switch: 100ms
- Dialog open/close: 300ms
- Loading spinner: 1000ms loop

## Icon Legend

- 📁 Folder (collapsed)
- 📂 Folder (expanded)
- 📄 File
- ⟳ Loading
- ✓ Success
- ✗ Error
- ⚠ Warning
- ℹ Info
- $ Command
- ● Active/Streaming

## Best Practices

### For Users
1. Wait for loading to complete before next action
2. Check Terminal tab for detailed logs
3. Save work before deploying
4. Review compilation errors before fixing

### For Developers
1. Always show loading states
2. Provide clear error messages
3. Log all operations to terminal
4. Handle edge cases gracefully

# CLI Workspace Architecture Diagram

## System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                         Browser (Client)                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌───────────────┐  ┌──────────────┐  ┌────────────────────┐   │
│  │  CLI Sidebar  │  │  File Tree   │  │  Monaco Editor     │   │
│  │  - Commands   │  │  - Folders   │  │  - Syntax Highlight│   │
│  │  - Categories │  │  - Files     │  │  - Code Editing    │   │
│  └───────┬───────┘  └──────┬───────┘  └─────────┬──────────┘   │
│          │                  │                     │              │
│          └──────────────────┴─────────────────────┘              │
│                             │                                    │
│                    ┌────────▼────────┐                          │
│                    │  Action Toolbar │                          │
│                    │  - Export       │                          │
│                    │  - GitHub       │                          │
│                    │  - Compile      │                          │
│                    │  - Deploy       │                          │
│                    └────────┬────────┘                          │
│                             │                                    │
└─────────────────────────────┼────────────────────────────────────┘
                              │
                    ┌─────────▼─────────┐
                    │   API Routes      │
                    │   (Next.js)       │
                    └─────────┬─────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
┌───────▼────────┐  ┌─────────▼────────┐  ┌────────▼────────┐
│ /api/projects  │  │ /api/contracts   │  │  /api/github    │
│ - files        │  │ - compile        │  │  - create-repo  │
└───────┬────────┘  │ - deploy         │  │  /api/auth      │
        │           └─────────┬────────┘  │  - github       │
        │                     │           └────────┬────────┘
        │                     │                    │
┌───────▼────────┐  ┌─────────▼────────┐  ┌────────▼────────┐
│  File System   │  │  Python Backend  │  │  GitHub API     │
│  flow_projects/│  │  FastAPI         │  │  OAuth + REST   │
└────────────────┘  │  /api/v1/flow    │  └─────────────────┘
                    └─────────┬────────┘
                              │
                    ┌─────────▼─────────┐
                    │    Flow CLI       │
                    │  - Compile        │
                    │  - Deploy         │
                    │  - Test           │
                    └───────────────────┘
```

## Component Interaction Flow

### 1. Contract Generation

```
User Input
    │
    ▼
Command Dialog
    │
    ▼
POST /api/contracts/submit
    │
    ▼
Python Backend
    │
    ├─► Generate Contract Code
    ├─► Create Project Structure
    ├─► Save to Database
    └─► Save to File System
    │
    ▼
Return project_path
    │
    ▼
Frontend Fetches Files
    │
    ▼
GET /api/projects/files?path=...
    │
    ▼
Read File System
    │
    ▼
Return File Tree
    │
    ▼
Display in UI
```

### 2. File Viewing

```
User Clicks File
    │
    ▼
Update selectedFile State
    │
    ▼
Monaco Editor Loads Content
    │
    ▼
Syntax Highlighting Applied
    │
    ▼
User Can Edit
```

### 3. Export Flow

```
User Clicks Export
    │
    ▼
Select Format (ZIP/TAR)
    │
    ▼
Client-Side Processing
    │
    ├─► Collect All Files
    ├─► Create Archive (JSZip)
    └─► Generate Blob
    │
    ▼
Trigger Download
```

### 4. GitHub Integration

```
User Clicks "Push to GitHub"
    │
    ▼
Check Authentication
    │
    ├─► Not Authenticated
    │   │
    │   ▼
    │   Redirect to GitHub OAuth
    │   │
    │   ▼
    │   User Authorizes
    │   │
    │   ▼
    │   Callback Stores Token
    │   │
    │   ▼
    │   Return to CLI Page
    │
    ▼
POST /api/github/create-repo
    │
    ├─► Create Repository (GitHub API)
    ├─► Upload Files (Parallel)
    └─► Return Repository URL
    │
    ▼
Open in New Tab
```

### 5. Compilation

```
User Clicks Compile
    │
    ▼
POST /api/contracts/compile
    │
    ├─► Create Temp File
    ├─► Run Flow CLI Check
    └─► Parse Output
    │
    ▼
Return Results
    │
    ▼
Display in Terminal Tab
```

### 6. Deployment

```
User Clicks Deploy
    │
    ▼
POST /api/contracts/deploy
    │
    ▼
Proxy to Python Backend
    │
    ▼
POST /api/v1/flow/deploy
    │
    ├─► Validate Project
    ├─► Run Flow CLI Deploy
    ├─► Track Transaction
    └─► Save to Database
    │
    ▼
Return Transaction ID
    │
    ▼
Display in Terminal Tab
```

## Data Models

### FileNode
```typescript
interface FileNode {
  name: string          // File/folder name
  path: string          // Relative path
  type: "file" | "directory"
  content?: string      // File content (if file)
  children?: FileNode[] // Child nodes (if directory)
}
```

### ProjectData
```typescript
interface ProjectData {
  projectPath: string   // Path on server
  projectId: string     // Unique identifier
  files: FileNode[]     // File tree
}
```

## State Management

```
┌─────────────────────────────────────┐
│         React State                 │
├─────────────────────────────────────┤
│ - selectedCommand: CLICommand       │
│ - dialogOpen: boolean               │
│ - files: FileNode[]                 │
│ - selectedFile: FileNode            │
│ - projectData: ProjectData          │
│ - expandedFolders: Set<string>      │
│ - isLoading: boolean                │
│ - isCompiling: boolean              │
│ - isDeploying: boolean              │
│ - isExporting: boolean              │
│ - executionHistory: any[]           │
│ - logs: TerminalLog[]               │
│ - isStreaming: boolean              │
└─────────────────────────────────────┘
```

## API Endpoints Summary

### Frontend (Next.js)

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/projects/files` | GET | Fetch project files |
| `/api/contracts/compile` | POST | Compile contract |
| `/api/contracts/deploy` | POST | Deploy contract |
| `/api/auth/github` | GET | Start OAuth |
| `/api/auth/github/callback` | GET | OAuth callback |
| `/api/github/create-repo` | POST | Create repository |

### Backend (Python)

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/v1/contracts/submit` | POST | Generate contract |
| `/api/v1/flow/deploy` | POST | Deploy to blockchain |
| `/api/v1/flow/projects` | GET | List projects |

## Security Layers

```
┌─────────────────────────────────────┐
│         Security Measures           │
├─────────────────────────────────────┤
│                                     │
│  1. Path Traversal Protection      │
│     - Restrict to flow_projects/   │
│     - Validate all paths           │
│                                     │
│  2. OAuth Token Security           │
│     - httpOnly cookies             │
│     - Secure flag in production    │
│     - 30-day expiration            │
│                                     │
│  3. Input Validation               │
│     - Type checking                │
│     - Schema validation            │
│     - Error handling               │
│                                     │
│  4. CORS Configuration             │
│     - Allowed origins              │
│     - Credential handling          │
│                                     │
│  5. Rate Limiting                  │
│     - API request limits           │
│     - GitHub API limits            │
│                                     │
└─────────────────────────────────────┘
```

## Technology Stack

```
┌─────────────────────────────────────┐
│           Frontend                  │
├─────────────────────────────────────┤
│ - Next.js 15                        │
│ - React 19                          │
│ - TypeScript                        │
│ - Monaco Editor                     │
│ - JSZip                             │
│ - Tailwind CSS                      │
│ - Radix UI                          │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│           Backend                   │
├─────────────────────────────────────┤
│ - Python 3.11+                      │
│ - FastAPI                           │
│ - SQLAlchemy                        │
│ - PostgreSQL                        │
│ - Pydantic                          │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│        External Services            │
├─────────────────────────────────────┤
│ - Flow Blockchain                   │
│ - Flow CLI                          │
│ - GitHub API                        │
│ - GitHub OAuth                      │
└─────────────────────────────────────┘
```

## Deployment Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Production                           │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌──────────────┐      ┌──────────────┐              │
│  │   Vercel     │      │   Railway    │              │
│  │  (Frontend)  │◄────►│  (Backend)   │              │
│  └──────┬───────┘      └──────┬───────┘              │
│         │                     │                        │
│         │                     ▼                        │
│         │              ┌──────────────┐               │
│         │              │  PostgreSQL  │               │
│         │              │  (Database)  │               │
│         │              └──────────────┘               │
│         │                                              │
│         ▼                                              │
│  ┌──────────────┐                                     │
│  │   GitHub     │                                     │
│  │   (OAuth)    │                                     │
│  └──────────────┘                                     │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

## Performance Optimization

```
┌─────────────────────────────────────┐
│      Optimization Strategies        │
├─────────────────────────────────────┤
│                                     │
│  1. Code Splitting                 │
│     - Dynamic Monaco import        │
│     - Lazy component loading       │
│                                     │
│  2. Client-Side Processing         │
│     - ZIP generation in browser    │
│     - File tree building           │
│                                     │
│  3. Parallel Operations            │
│     - GitHub file uploads          │
│     - Multiple API calls           │
│                                     │
│  4. Caching                        │
│     - File content caching         │
│     - API response caching         │
│                                     │
│  5. Async Operations               │
│     - Non-blocking UI updates      │
│     - Background processing        │
│                                     │
└─────────────────────────────────────┘
```

## Error Handling Flow

```
Error Occurs
    │
    ▼
Catch in Try-Catch
    │
    ▼
Log to Console
    │
    ▼
Display in Terminal Tab
    │
    ▼
Show User-Friendly Message
    │
    ▼
Provide Recovery Options
```

## Monitoring Points

```
┌─────────────────────────────────────┐
│         Monitoring Metrics          │
├─────────────────────────────────────┤
│                                     │
│  - API Response Times              │
│  - Error Rates                     │
│  - User Actions                    │
│  - File Generation Success         │
│  - Compilation Success Rate        │
│  - Deployment Success Rate         │
│  - GitHub Integration Usage        │
│  - Export Downloads                │
│                                     │
└─────────────────────────────────────┘
```

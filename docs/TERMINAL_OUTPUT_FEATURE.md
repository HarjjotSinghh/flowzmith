# Terminal Output Feature

## Overview

The CLI workspace now includes a **real-time terminal output** feature that streams command execution logs, similar to build logs on Vercel, Cloudflare, or Netlify.

## Features

### ✅ Real-Time Streaming
- Live output as commands execute
- Server-Sent Events (SSE) support
- Automatic scrolling to latest logs
- Streaming indicator

### ✅ Timestamped Logs
- Millisecond precision timestamps
- Color-coded log types
- Emoji indicators for quick scanning

### ✅ Log Types
- **Info** (ℹ️) - General information
- **Success** (✅) - Successful operations
- **Error** (❌) - Errors and failures
- **Warning** (⚠️) - Warnings
- **Command** (▶) - Command execution

### ✅ Terminal Controls
- Auto-scroll toggle
- Clear logs button
- Line count display
- Streaming status indicator

## Usage

### 1. Execute a Command

Click any command in the sidebar and execute it. The terminal will automatically:
1. Log the command being executed
2. Stream real-time output
3. Show completion status

### 2. View Terminal Output

Switch to the **Terminal** tab to see:
```
12:34:56.789 ▶ Executing command: Create Contract
12:34:56.790 ℹ️ Parameters: { "requirements": "..." }
12:34:56.791 ℹ️ Calling API endpoint: POST /api/contracts/submit
12:34:57.123 ℹ️ Receiving streaming response...
12:34:57.456 ℹ️ Generating contract...
12:34:58.789 ✅ Contract generated successfully
12:34:58.790 ✅ Command completed successfully
```

### 3. Control Auto-Scroll

- **Auto-scroll ON**: Terminal automatically scrolls to show latest logs
- **Auto-scroll OFF**: You can scroll freely to review older logs

### 4. Clear Logs

Click the **X** button in the terminal header to clear all logs.

## For Streaming Commands

Commands that support streaming (marked with `"streaming": true` in config) will:

1. **Stream output in real-time** - Each chunk appears as it's received
2. **Show progress updates** - Status messages during execution
3. **Display errors immediately** - No waiting for completion
4. **Provide detailed feedback** - Step-by-step execution details

### Example: Generate from Context

```json
{
  "id": "generate_from_context",
  "streaming": true,
  "endpoint": "/api/contract/generate/stream"
}
```

When executed, you'll see:
```
12:34:56.789 ▶ Executing command: Generate from Context
12:34:56.790 ℹ️ Calling API endpoint: POST /api/contract/generate/stream
12:34:56.791 ℹ️ Receiving streaming response...
12:34:57.123 ℹ️ Reading context files...
12:34:57.456 ℹ️ Analyzing requirements...
12:34:58.123 ℹ️ Generating contract structure...
12:34:59.456 ℹ️ Adding contract logic...
12:35:00.789 ℹ️ Validating contract...
12:35:01.123 ✅ Contract generation completed
12:35:01.124 ✅ Generated contract code received
12:35:01.125 ℹ️ Contract name: MyContract
12:35:01.126 ✅ Files added to workspace
12:35:01.127 ✅ Command "Generate from Context" completed successfully
```

## For Non-Streaming Commands

Regular commands will show:
1. Command execution start
2. API call details
3. Response received
4. Completion status

### Example: List Deployments

```
12:34:56.789 ▶ Executing command: List Deployments
12:34:56.790 ℹ️ Calling API endpoint: GET /api/deployments
12:34:57.123 ✅ Response received
12:34:57.124 ℹ️ { "deployments": [...] }
12:34:57.125 ✅ Command "List Deployments" completed successfully
```

## Implementation Details

### Terminal Component

Located at: `flowZmith/components/cli/terminal-output.tsx`

Features:
- Virtualized scrolling for performance
- Auto-scroll with manual override
- Color-coded log types
- Timestamp formatting
- Clear functionality

### Hook: useTerminalLogs

```typescript
const { 
  logs,           // Array of log entries
  isStreaming,    // Streaming status
  addLog,         // Add a log entry
  clearLogs,      // Clear all logs
  startStreaming, // Start streaming mode
  stopStreaming   // Stop streaming mode
} = useTerminalLogs()
```

### Log Entry Structure

```typescript
interface LogEntry {
  timestamp: Date
  message: string
  type: "info" | "error" | "success" | "warning" | "command"
}
```

## Backend Integration

### Streaming Endpoint Example

```typescript
// app/api/contract/generate/stream/route.ts
export async function POST(request: NextRequest) {
  const encoder = new TextEncoder()
  
  const stream = new ReadableStream({
    async start(controller) {
      // Send progress updates
      controller.enqueue(
        encoder.encode(`data: ${JSON.stringify({
          type: "progress",
          data: { message: "Starting generation..." }
        })}\n\n`)
      )
      
      // ... more updates ...
      
      // Send completion
      controller.enqueue(
        encoder.encode(`data: ${JSON.stringify({
          type: "complete",
          data: { status: "success" }
        })}\n\n`)
      )
      
      controller.close()
    }
  })
  
  return new Response(stream, {
    headers: {
      'Content-Type': 'text/event-stream',
      'Cache-Control': 'no-cache',
      'Connection': 'keep-alive',
    }
  })
}
```

### Message Types

The terminal recognizes these message types:

```typescript
// Content/output
{ type: "content", chunk: "message" }

// Error
{ type: "error", error: "error message" }

// Status update
{ type: "status", data: { stage: "Processing..." } }

// Progress update
{ type: "progress", data: { message: "50% complete" } }

// Completion
{ type: "complete", data: { status: "success" } }
```

## Styling

The terminal uses a dark theme with:
- **Background**: Black (`bg-black`)
- **Header/Footer**: Dark gray (`bg-gray-900`)
- **Text**: Light gray (`text-gray-300`)
- **Timestamps**: Muted gray (`text-gray-500`)
- **Success**: Green (`text-green-400`)
- **Error**: Red (`text-red-400`)
- **Warning**: Yellow (`text-yellow-400`)
- **Command**: Blue (`text-blue-400`)

## Performance

- **Efficient rendering**: Only visible logs are rendered
- **Auto-scroll optimization**: Scroll only when needed
- **Memory management**: Consider limiting log history for long-running commands

## Future Enhancements

- [ ] Log filtering by type
- [ ] Search within logs
- [ ] Export logs to file
- [ ] Log persistence across sessions
- [ ] Multiple terminal tabs
- [ ] Log highlighting/bookmarks
- [ ] Keyboard shortcuts

## Tips

1. **Keep auto-scroll ON** for real-time monitoring
2. **Turn auto-scroll OFF** to review specific logs
3. **Clear logs** before running new commands for clarity
4. **Watch the streaming indicator** to know when output is live
5. **Check timestamps** to identify slow operations

## Troubleshooting

### Logs not appearing?

1. Check if command has `"streaming": true` in config
2. Verify endpoint returns Server-Sent Events
3. Check browser console for errors
4. Ensure API endpoint is correct

### Auto-scroll not working?

1. Click "Auto-scroll: ON" button
2. Check if you manually scrolled (disables auto-scroll)
3. Try clearing logs and re-executing

### Streaming indicator stuck?

1. Command may have failed silently
2. Check browser network tab
3. Verify API endpoint is responding
4. Try refreshing the page

## Summary

The terminal output feature provides:
- ✅ Real-time command execution feedback
- ✅ Professional build-log-like experience
- ✅ Color-coded, timestamped logs
- ✅ Streaming support for long operations
- ✅ Full control over display and scrolling

**Perfect for monitoring CLI command execution!** 🚀

# Testing Checklist for CLI Workspace

## Pre-Testing Setup

- [ ] Backend server running on port 8000
- [ ] Frontend server running on port 3001
- [ ] Flow CLI installed and in PATH
- [ ] PostgreSQL database connected
- [ ] Environment variables configured
- [ ] GitHub OAuth credentials set (optional)

## Feature Testing

### 1. Contract Generation
- [ ] Click "Create Contract" in sidebar
- [ ] Fill in contract name
- [ ] Fill in description
- [ ] Select network (testnet/mainnet/emulator)
- [ ] Check feature checkboxes
- [ ] Click "Execute"
- [ ] Loading overlay appears
- [ ] Loading overlay shows status message
- [ ] Generation completes successfully
- [ ] Files appear in file tree
- [ ] Main contract opens in editor
- [ ] Terminal shows success logs

### 2. File Tree Navigation
- [ ] File tree appears after generation
- [ ] Folders show with folder icon
- [ ] Files show with file icon
- [ ] Click folder to expand
- [ ] Folder expands with animation
- [ ] Click folder again to collapse
- [ ] Folder collapses with animation
- [ ] Nested folders indent properly
- [ ] Click file to open
- [ ] File opens in editor
- [ ] Selected file highlights
- [ ] Multiple files can be opened sequentially

### 3. Monaco Editor
- [ ] Editor loads without errors
- [ ] Syntax highlighting works for .cdc files
- [ ] Syntax highlighting works for .json files
- [ ] Line numbers display
- [ ] Dark theme applied
- [ ] Can type and edit code
- [ ] Auto-completion works
- [ ] Find/replace works (Ctrl+F)
- [ ] Code folding works
- [ ] Minimap is disabled
- [ ] Font size is readable

### 4. Export as ZIP
- [ ] Click "Export" dropdown
- [ ] "Export as .zip" option visible
- [ ] Click "Export as .zip"
- [ ] Loading state shows on button
- [ ] Terminal logs "Creating ZIP archive..."
- [ ] ZIP file downloads
- [ ] ZIP file has correct name
- [ ] Extract ZIP locally
- [ ] All files present in ZIP
- [ ] Folder structure preserved
- [ ] File contents correct

### 5. Export as TAR
- [ ] Click "Export" dropdown
- [ ] "Export as .tar" option visible
- [ ] Click "Export as .tar"
- [ ] Loading state shows on button
- [ ] Terminal logs "Creating TAR archive..."
- [ ] TAR file downloads
- [ ] TAR file has correct name
- [ ] TAR file contains all files

### 6. GitHub Integration (OAuth)
- [ ] Click "Push to GitHub" button
- [ ] Redirects to GitHub OAuth
- [ ] GitHub authorization page loads
- [ ] Click "Authorize" on GitHub
- [ ] Redirects back to CLI page
- [ ] URL shows "github_connected=true"
- [ ] Terminal logs "GitHub connected successfully"
- [ ] Repository creation starts automatically

### 7. GitHub Integration (Repo Creation)
- [ ] Terminal logs "Creating GitHub repository..."
- [ ] Repository name generated
- [ ] Files uploaded to GitHub
- [ ] Terminal shows progress
- [ ] Terminal logs repository URL
- [ ] Repository opens in new tab
- [ ] All files present in repository
- [ ] Folder structure preserved
- [ ] README.md displays correctly

### 8. Compile Contract
- [ ] Select a .cdc file
- [ ] "Compile" button appears
- [ ] "Compile" button is enabled
- [ ] Click "Compile" button
- [ ] Button shows loading state
- [ ] Terminal logs "Compiling..."
- [ ] Compilation completes
- [ ] Terminal shows success or errors
- [ ] Errors are readable and helpful
- [ ] Warnings displayed if any
- [ ] Button returns to normal state

### 9. Deploy Contract
- [ ] Select a .cdc file
- [ ] "Deploy On-Chain" button appears
- [ ] "Deploy On-Chain" button is enabled
- [ ] Click "Deploy On-Chain" button
- [ ] Button shows loading state
- [ ] Terminal logs "Deploying..."
- [ ] Deployment completes
- [ ] Terminal shows transaction ID
- [ ] Terminal shows contract address
- [ ] Success message displayed
- [ ] Button returns to normal state

### 10. Terminal Output
- [ ] Terminal tab accessible
- [ ] Logs display in chronological order
- [ ] Command logs show in blue
- [ ] Info logs show in gray
- [ ] Success logs show in green
- [ ] Warning logs show in yellow
- [ ] Error logs show in red
- [ ] Auto-scroll works
- [ ] "Clear" button works
- [ ] Streaming indicator shows when active

### 11. History Tab
- [ ] History tab accessible
- [ ] Executed commands appear
- [ ] Newest commands at top
- [ ] Timestamp displays correctly
- [ ] Status badge shows correct status
- [ ] Success commands show green badge
- [ ] Failed commands show red badge
- [ ] Project path displays if available
- [ ] Transaction ID displays if available

### 12. Loading States
- [ ] Loading overlay shows during generation
- [ ] Overlay prevents interaction
- [ ] Spinner animates smoothly
- [ ] Status message displays
- [ ] Export button shows spinner when exporting
- [ ] Compile button shows spinner when compiling
- [ ] Deploy button shows spinner when deploying
- [ ] Buttons disable during operations

## Error Handling

### Network Errors
- [ ] Backend offline - shows error message
- [ ] API timeout - shows timeout error
- [ ] Invalid response - shows parse error
- [ ] Network disconnected - shows connection error

### Validation Errors
- [ ] Empty contract name - shows validation error
- [ ] Invalid characters - shows validation error
- [ ] Missing required fields - shows which fields

### File System Errors
- [ ] Project not found - shows error message
- [ ] File read error - shows error message
- [ ] Permission denied - shows error message

### Compilation Errors
- [ ] Syntax error - shows error location
- [ ] Type error - shows error details
- [ ] Flow CLI not found - shows installation help

### Deployment Errors
- [ ] No account configured - shows setup help
- [ ] Network error - shows network status
- [ ] Transaction failed - shows failure reason

### GitHub Errors
- [ ] OAuth failed - shows retry option
- [ ] Token expired - prompts re-authentication
- [ ] Repository exists - shows error message
- [ ] Upload failed - shows which files failed

## Performance Testing

### Load Times
- [ ] Page loads in < 2 seconds
- [ ] File tree loads in < 1 second
- [ ] Editor loads in < 1 second
- [ ] File opens in < 500ms

### Responsiveness
- [ ] UI remains responsive during generation
- [ ] No lag when typing in editor
- [ ] Smooth folder expand/collapse
- [ ] Smooth tab switching

### Memory Usage
- [ ] No memory leaks after multiple operations
- [ ] Browser doesn't slow down over time
- [ ] Large files (>1MB) load without issues

## Browser Compatibility

### Chrome
- [ ] All features work
- [ ] UI renders correctly
- [ ] No console errors

### Firefox
- [ ] All features work
- [ ] UI renders correctly
- [ ] No console errors

### Safari
- [ ] All features work
- [ ] UI renders correctly
- [ ] No console errors

### Edge
- [ ] All features work
- [ ] UI renders correctly
- [ ] No console errors

## Accessibility

### Keyboard Navigation
- [ ] Tab through all elements
- [ ] Enter activates buttons
- [ ] Escape closes dialogs
- [ ] Arrow keys navigate file tree

### Screen Reader
- [ ] Buttons have ARIA labels
- [ ] Status messages announced
- [ ] Error messages announced
- [ ] Success messages announced

### Visual
- [ ] Sufficient color contrast
- [ ] Focus indicators visible
- [ ] Text is readable
- [ ] Icons have tooltips

## Security Testing

### Path Traversal
- [ ] Cannot access files outside flow_projects/
- [ ] Path validation works
- [ ] Error message doesn't leak paths

### OAuth Security
- [ ] Tokens stored in httpOnly cookies
- [ ] Tokens not visible in JavaScript
- [ ] Tokens expire correctly
- [ ] CSRF protection works

### Input Validation
- [ ] SQL injection prevented
- [ ] XSS attacks prevented
- [ ] Command injection prevented
- [ ] File upload validation works

## Edge Cases

### Empty States
- [ ] No files - shows empty state message
- [ ] No history - shows empty state message
- [ ] No logs - shows empty state message

### Large Projects
- [ ] 100+ files load correctly
- [ ] File tree remains responsive
- [ ] Search works with many files

### Special Characters
- [ ] File names with spaces work
- [ ] File names with unicode work
- [ ] Contract names with special chars handled

### Network Issues
- [ ] Slow connection - shows loading
- [ ] Connection drops - shows error
- [ ] Reconnection works

## Regression Testing

### After Updates
- [ ] All existing features still work
- [ ] No new console errors
- [ ] No broken UI elements
- [ ] Performance not degraded

## User Acceptance Testing

### First-Time User
- [ ] Can generate contract without help
- [ ] UI is intuitive
- [ ] Error messages are helpful
- [ ] Success feedback is clear

### Power User
- [ ] Keyboard shortcuts work
- [ ] Workflow is efficient
- [ ] No unnecessary clicks
- [ ] Fast operations

## Documentation Testing

### Setup Guide
- [ ] Instructions are clear
- [ ] All steps work
- [ ] No missing information
- [ ] Examples are correct

### Feature Guide
- [ ] All features documented
- [ ] Screenshots are accurate
- [ ] Code examples work
- [ ] Links are valid

### API Documentation
- [ ] Endpoints documented
- [ ] Request examples work
- [ ] Response examples accurate
- [ ] Error codes documented

## Final Checks

- [ ] All tests passed
- [ ] No critical bugs
- [ ] Performance acceptable
- [ ] Documentation complete
- [ ] Ready for production

## Sign-Off

**Tested By**: ___________________
**Date**: ___________________
**Version**: ___________________
**Status**: [ ] Pass [ ] Fail
**Notes**: ___________________

---

## Bug Report Template

If you find a bug, report it with:

1. **Description**: What happened?
2. **Expected**: What should happen?
3. **Steps to Reproduce**:
   - Step 1
   - Step 2
   - Step 3
4. **Environment**:
   - Browser: 
   - OS: 
   - Version: 
5. **Screenshots**: (if applicable)
6. **Console Errors**: (if any)
7. **Severity**: Critical / High / Medium / Low

## Feature Request Template

If you have a feature request:

1. **Feature**: What feature do you want?
2. **Use Case**: Why do you need it?
3. **Benefit**: How will it help?
4. **Priority**: High / Medium / Low
5. **Mockup**: (if applicable)

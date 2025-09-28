# Fix for "UnknownAction: Unsupported action" Error

## 🔍 **Root Cause Analysis**

The error `UnknownAction: Unsupported action` occurs when:
1. **Environment variables are missing** - GitHub OAuth credentials not set
2. **NextAuth configuration is invalid** - Providers array is empty
3. **API routes not properly configured** - Auth handlers not working

## ✅ **Fixes Applied**

### **1. Enhanced Environment Variable Validation**
```typescript
// lib/auth.ts - Added validation warnings
if (!process.env.GITHUB_CLIENT_ID) {
  console.warn("GITHUB_CLIENT_ID is not set")
}
if (!process.env.GITHUB_CLIENT_SECRET) {
  console.warn("GITHUB_CLIENT_SECRET is not set")
}
if (!process.env.NEXTAUTH_SECRET) {
  console.warn("NEXTAUTH_SECRET is not set")
}
```

### **2. Conditional Provider Configuration**
```typescript
// Only add GitHub provider if credentials are available
providers: [
  ...(process.env.GITHUB_CLIENT_ID && process.env.GITHUB_CLIENT_SECRET ? [
    GitHub({
      clientId: process.env.GITHUB_CLIENT_ID,
      clientSecret: process.env.GITHUB_CLIENT_SECRET,
    })
  ] : []),
],
```

### **3. Debug Page Created**
- **URL**: `http://localhost:3000/debug-auth`
- **Features**: Environment check, session status, quick actions
- **Purpose**: Help diagnose authentication issues

## 🚀 **Immediate Steps to Fix**

### **Step 1: Create Environment File**
Create `.env.local` in your project root:
```env
NEXTAUTH_URL=http://localhost:3000
NEXTAUTH_SECRET=your-secret-key-here
GITHUB_CLIENT_ID=your-github-client-id
GITHUB_CLIENT_SECRET=your-github-client-secret
```

### **Step 2: Generate NextAuth Secret**
```bash
# Option 1: Using OpenSSL
openssl rand -base64 32

# Option 2: Using Node.js
node -e "console.log(require('crypto').randomBytes(32).toString('base64'))"

# Option 3: Online generator
# Visit: https://generate-secret.vercel.app/32
```

### **Step 3: Set up GitHub OAuth App**
1. Go to [GitHub Developer Settings](https://github.com/settings/developers)
2. Click "New OAuth App"
3. Fill in:
   - **Application name**: `Flow Builder Dashboard`
   - **Homepage URL**: `http://localhost:3000`
   - **Authorization callback URL**: `http://localhost:3000/api/auth/callback/github`
4. Copy Client ID and generate Client Secret

### **Step 4: Test the Fix**
1. **Visit**: `http://localhost:3000/debug-auth`
2. **Check**: All environment variables show "✅ Set"
3. **Test**: Click "Test GitHub Sign In"
4. **Verify**: Redirect to GitHub OAuth page

## 🔧 **Debug Commands**

### **Check Environment Variables**
```bash
# In your terminal
echo $GITHUB_CLIENT_ID
echo $GITHUB_CLIENT_SECRET
echo $NEXTAUTH_SECRET
```

### **Test NextAuth API**
```bash
# Check providers
curl http://localhost:3000/api/auth/providers

# Check session
curl http://localhost:3000/api/auth/session
```

### **Check Server Logs**
Look for these warnings in your terminal:
- `GITHUB_CLIENT_ID is not set`
- `GITHUB_CLIENT_SECRET is not set`
- `NEXTAUTH_SECRET is not set`

## 📋 **Verification Checklist**

- [ ] `.env.local` file created with all variables
- [ ] GitHub OAuth App created with correct callback URL
- [ ] NextAuth secret generated and set
- [ ] Development server restarted after env changes
- [ ] Debug page shows all green checkmarks
- [ ] No warnings in server console
- [ ] `/api/auth/providers` returns GitHub provider

## 🆘 **If Still Not Working**

### **Check 1: Environment Variables**
Visit `http://localhost:3000/debug-auth` and ensure all variables show "✅ Set"

### **Check 2: GitHub OAuth App**
- Callback URL must be exactly: `http://localhost:3000/api/auth/callback/github`
- No trailing slashes or different ports
- App must be active (not suspended)

### **Check 3: NextAuth Configuration**
- Providers array should not be empty
- No TypeScript errors in `lib/auth.ts`
- API routes properly configured

### **Check 4: Server Restart**
After setting environment variables:
```bash
# Stop the server (Ctrl+C)
# Then restart
npm run dev
```

## 🎯 **Expected Result**

After fixing the environment variables:
1. **No more "UnknownAction" errors**
2. **GitHub OAuth flow works**
3. **Successful redirect to dashboard**
4. **Session properly established**

The authentication should now work correctly! 🎉

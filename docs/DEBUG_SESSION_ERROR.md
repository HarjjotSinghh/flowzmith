# Fix for "Unexpected token '<'" Session Error

## 🔍 **Root Cause Analysis**

The error `Unexpected token '<', "<!DOCTYPE "... is not valid JSON` occurs when:
1. **NextAuth.js session endpoint returns HTML instead of JSON**
2. **API route is not properly configured**
3. **Environment variables are missing**
4. **NextAuth.js configuration is invalid**

## ✅ **Fixes Applied**

### **1. Enhanced Auth Configuration**
- Added conditional provider loading
- Added environment variable debugging
- Improved error handling

### **2. Created Test Endpoints**
- `/api/test` - Basic API functionality test
- `/api/session-test` - Session debugging endpoint

### **3. Added Debug Logging**
- Console logs for environment variables
- Better error messages
- Session status verification

## 🧪 **Debugging Steps**

### **Step 1: Check Basic API Functionality**
Visit: `http://localhost:3000/api/test`
- Should return JSON with environment status
- If this fails, there's a basic API issue

### **Step 2: Check Session Endpoint**
Visit: `http://localhost:3000/api/session-test`
- Should return JSON with session information
- Check environment variables status

### **Step 3: Check NextAuth Endpoints**
Visit: `http://localhost:3000/api/auth/session`
- Should return JSON (not HTML)
- If HTML is returned, there's a NextAuth configuration issue

### **Step 4: Check Providers**
Visit: `http://localhost:3000/api/auth/providers`
- Should return available providers
- Should include GitHub if configured correctly

## 🔧 **Common Solutions**

### **Solution 1: Environment Variables Missing**
Create `.env.local` in project root:
```env
NEXTAUTH_URL=http://localhost:3000
NEXTAUTH_SECRET=your-secret-key-here
GITHUB_CLIENT_ID=your-github-client-id
GITHUB_CLIENT_SECRET=your-github-client-secret
```

### **Solution 2: Restart Development Server**
After setting environment variables:
```bash
# Stop server (Ctrl+C)
npm run dev
```

### **Solution 3: Check Console Logs**
Look for these debug messages in your terminal:
```
Auth Debug: {
  hasGithubClientId: true/false,
  hasGithubClientSecret: true/false,
  hasNextAuthSecret: true/false,
  nextAuthUrl: "http://localhost:3000"
}
```

### **Solution 4: Verify API Route Structure**
Ensure the file structure is correct:
```
app/
  api/
    auth/
      [...nextauth]/
        route.ts
```

## 📋 **Verification Checklist**

- [ ] `.env.local` file exists with all variables
- [ ] Development server restarted after env changes
- [ ] `/api/test` returns JSON
- [ ] `/api/session-test` returns JSON
- [ ] `/api/auth/session` returns JSON
- [ ] `/api/auth/providers` shows GitHub provider
- [ ] No HTML responses from API endpoints
- [ ] Console shows environment debug info

## 🚀 **Expected Results**

### **Working Configuration:**
```json
// /api/test response
{
  "message": "API is working",
  "environment": {
    "hasGithubClientId": true,
    "hasGithubClientSecret": true,
    "hasNextAuthSecret": true,
    "nextAuthUrl": "http://localhost:3000"
  }
}
```

### **Working Session:**
```json
// /api/auth/session response
{
  "user": {
    "name": "Your Name",
    "email": "your@email.com",
    "image": "https://avatar-url"
  },
  "expires": "2024-01-01T00:00:00.000Z"
}
```

## 🆘 **If Still Not Working**

1. **Check browser console** for specific error messages
2. **Check server console** for environment debug logs
3. **Verify file structure** matches NextAuth.js requirements
4. **Test each endpoint** individually
5. **Clear browser cache** and try again

The session error should be resolved once environment variables are properly set! 🎉

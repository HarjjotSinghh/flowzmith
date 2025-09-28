# Complete GitHub OAuth Setup Guide

## 🎯 **Current Status**
✅ You're successfully reaching the GitHub OAuth URL!  
✅ NextAuth.js is working correctly  
❌ Need to complete GitHub OAuth App setup  

## 📋 **Next Steps to Complete Setup**

### **Step 1: Create GitHub OAuth App**

1. **Go to GitHub Developer Settings**
   - Visit: https://github.com/settings/developers
   - Click "OAuth Apps" in the left sidebar
   - Click "New OAuth App"

2. **Fill in the OAuth App Details**
   ```
   Application name: Flow Builder Dashboard
   Homepage URL: http://localhost:3000
   Application description: AI-powered smart contract builder
   Authorization callback URL: http://localhost:3000/api/auth/callback/github
   ```

3. **Important**: Make sure the callback URL is exactly:
   ```
   http://localhost:3000/api/auth/callback/github
   ```
   - No trailing slash
   - Port 3000 (not 3002)
   - Exact path `/api/auth/callback/github`

### **Step 2: Get Your Credentials**

After creating the OAuth App:

1. **Copy the Client ID** (visible immediately)
2. **Generate Client Secret**:
   - Click "Generate a new client secret"
   - Copy the secret (you won't see it again!)

### **Step 3: Set Environment Variables**

Create `.env.local` in your project root:

```env
# NextAuth Configuration
NEXTAUTH_URL=http://localhost:3000
NEXTAUTH_SECRET=your-secret-key-here

# GitHub OAuth Credentials
GITHUB_CLIENT_ID=your-github-client-id
GITHUB_CLIENT_SECRET=your-github-client-secret
```

### **Step 4: Generate NextAuth Secret**

Run this command to generate a secure secret:
```bash
openssl rand -base64 32
```

Or use an online generator: https://generate-secret.vercel.app/32

### **Step 5: Restart Your Development Server**

After setting environment variables:
```bash
# Stop the server (Ctrl+C)
npm run dev
```

## 🧪 **Testing the Complete Flow**

### **Test 1: Environment Check**
Visit: `http://localhost:3000/debug-auth`
- All variables should show "✅ Set"
- No red error messages

### **Test 2: GitHub OAuth Flow**
1. Go to: `http://localhost:3000/login`
2. Click "Continue with GitHub"
3. You should be redirected to GitHub
4. Authorize the application
5. You should be redirected back to `/dashboard`

### **Test 3: Verify Session**
After successful login:
- Check `http://localhost:3000/api/auth/session`
- Should return your user information

## 🔧 **Troubleshooting**

### **Issue: "Invalid redirect URI"**
**Solution**: Check GitHub OAuth App callback URL
- Must be exactly: `http://localhost:3000/api/auth/callback/github`
- No trailing slash, correct port (3000)

### **Issue: "Client ID not found"**
**Solution**: Check environment variables
- Ensure `.env.local` exists in project root
- Restart development server after changes
- Check variable names are correct

### **Issue: Still getting "UnknownAction" error**
**Solution**: Verify all environment variables are set
- Visit `http://localhost:3000/debug-auth`
- All should show green checkmarks

## 📱 **Expected Complete Flow**

1. **Click Login** → Redirect to GitHub OAuth
2. **GitHub Authorization** → User authorizes app
3. **Callback to NextAuth** → `http://localhost:3000/api/auth/callback/github`
4. **Session Created** → User data stored
5. **Redirect to Dashboard** → `http://localhost:3000/dashboard`

## ✅ **Success Indicators**

- ✅ No "UnknownAction" errors in console
- ✅ GitHub OAuth page loads correctly
- ✅ After authorization, redirects to dashboard
- ✅ User session is established
- ✅ Dashboard loads with user information

## 🚀 **You're Almost There!**

The hard part (NextAuth configuration) is done. You just need to:
1. Create the GitHub OAuth App
2. Set the environment variables
3. Restart your server

Then the authentication will work perfectly! 🎉

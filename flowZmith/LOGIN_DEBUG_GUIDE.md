# Login Redirect Debug Guide

## 🔧 **Fixes Applied**

### **1. Updated Login Logic**
- **Before**: Used `redirect: false` with manual navigation
- **After**: Using direct window.location redirect to NextAuth endpoint
- **Why**: More reliable and follows NextAuth best practices

### **2. Alternative Login Method**
```typescript
const handleGithubLoginAlternative = () => {
  setIsLoading(true)
  console.log("Using alternative login method...")
  
  // Direct redirect to NextAuth GitHub provider
  window.location.href = "/api/auth/signin/github?callbackUrl=/dashboard"
}
```

### **3. Added Debug Logging**
- Console logs to track login flow
- Error handling for debugging
- Test endpoint at `/api/test-auth`

## 🧪 **Testing Steps**

### **Step 1: Check Environment Variables**
Visit: `http://localhost:3000/api/test-auth`

This will show you:
- ✅ If GitHub OAuth credentials are set
- ✅ If NextAuth secret is configured
- ✅ Current session status

### **Step 2: Test Login Flow**
1. Go to `http://localhost:3000/login`
2. Open browser console (F12)
3. Click "Continue with GitHub"
4. Check console for logs:
   - "Using alternative login method..."
   - Any error messages

### **Step 3: Verify GitHub OAuth Setup**
Make sure your GitHub OAuth App has:
- **Authorization callback URL**: `http://localhost:3000/api/auth/callback/github`
- **Homepage URL**: `http://localhost:3000`

## 🔍 **Common Issues & Solutions**

### **Issue 1: "Invalid redirect URI"**
**Solution**: Check GitHub OAuth App settings
- Callback URL must be exactly: `http://localhost:3000/api/auth/callback/github`
- No trailing slashes or different ports

### **Issue 2: "Client ID not found"**
**Solution**: Check environment variables
```bash
# In your .env.local file
GITHUB_CLIENT_ID=your_actual_client_id
GITHUB_CLIENT_SECRET=your_actual_client_secret
NEXTAUTH_SECRET=your_secret_key
NEXTAUTH_URL=http://localhost:3000
```

### **Issue 3: No redirect after GitHub authorization**
**Solution**: Check browser console for errors
- Look for CORS issues
- Check if GitHub OAuth is properly configured
- Verify callback URL matches exactly

## 🚀 **Expected Flow**

1. **Click Login Button** → Console shows "Using alternative login method..."
2. **Redirect to GitHub** → `https://github.com/login/oauth/authorize?...`
3. **GitHub Authorization** → User authorizes the app
4. **Callback to NextAuth** → `http://localhost:3000/api/auth/callback/github?...`
5. **Redirect to Dashboard** → `http://localhost:3000/dashboard`

## 🛠️ **Debug Commands**

### **Check if NextAuth is working:**
```bash
curl http://localhost:3000/api/auth/providers
```

### **Check environment variables:**
```bash
# In your terminal
echo $GITHUB_CLIENT_ID
echo $GITHUB_CLIENT_SECRET
echo $NEXTAUTH_SECRET
```

### **Test GitHub OAuth directly:**
Visit: `http://localhost:3000/api/auth/signin/github`

## 📋 **Checklist**

- [ ] GitHub OAuth App created
- [ ] Callback URL set to: `http://localhost:3000/api/auth/callback/github`
- [ ] Environment variables in `.env.local`
- [ ] Development server running on port 3000
- [ ] No CORS errors in browser console
- [ ] NextAuth API routes accessible

## 🆘 **If Still Not Working**

1. **Check browser console** for specific error messages
2. **Visit `/api/test-auth`** to verify environment setup
3. **Try direct NextAuth URL**: `http://localhost:3000/api/auth/signin/github`
4. **Check GitHub OAuth App** settings match exactly
5. **Restart development server** after environment changes

The login should now work with the direct redirect approach! 🎉

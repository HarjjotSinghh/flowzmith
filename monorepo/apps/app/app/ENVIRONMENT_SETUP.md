# Environment Setup for GitHub OAuth

## 🔧 **Required Environment Variables**

Create a `.env.local` file in your project root with the following variables:

```env
# NextAuth Configuration
NEXTAUTH_URL=http://localhost:3000
NEXTAUTH_SECRET=your-secret-key-here

# GitHub OAuth Credentials
GITHUB_CLIENT_ID=your-github-client-id
GITHUB_CLIENT_SECRET=your-github-client-secret
```

## 📋 **Step-by-Step Setup**

### **Step 1: Generate NextAuth Secret**
```bash
# Using OpenSSL
openssl rand -base64 32

# Using Node.js
node -e "console.log(require('crypto').randomBytes(32).toString('base64'))"

# Or use online generator: https://generate-secret.vercel.app/32
```

### **Step 2: Create GitHub OAuth App**

1. **Go to GitHub Developer Settings**
   - Visit: https://github.com/settings/developers
   - Click "OAuth Apps" → "New OAuth App"

2. **Fill in the details**:
   ```
   Application name: Flow Builder Dashboard
   Homepage URL: http://localhost:3000
   Application description: AI-powered smart contract builder
   Authorization callback URL: http://localhost:3000/api/auth/callback/github
   ```

3. **Important**: The callback URL must be exactly:
   ```
   http://localhost:3000/api/auth/callback/github
   ```

### **Step 3: Get Your Credentials**

After creating the OAuth App:
1. **Copy the Client ID** (visible immediately)
2. **Generate Client Secret**:
   - Click "Generate a new client secret"
   - Copy the secret (you won't see it again!)

### **Step 4: Update Environment Variables**

Replace the placeholder values in `.env.local`:
```env
NEXTAUTH_URL=http://localhost:3000
NEXTAUTH_SECRET=your-actual-secret-here
GITHUB_CLIENT_ID=your-actual-client-id
GITHUB_CLIENT_SECRET=your-actual-client-secret
```

### **Step 5: Restart Development Server**

```bash
# Stop the server (Ctrl+C)
npm run dev
```

## 🧪 **Testing the Setup**

### **Test 1: Check Environment Variables**
Visit: `http://localhost:3000/debug-auth`
- All variables should show "✅ Set"

### **Test 2: Test GitHub OAuth**
1. Go to: `http://localhost:3000/login`
2. Click "Continue with GitHub"
3. You should be redirected to GitHub
4. Authorize the application
5. You should be redirected to `/dashboard`

### **Test 3: Verify Session**
After successful login:
- Check: `http://localhost:3000/api/auth/session`
- Should return your user information

## 🔍 **Troubleshooting**

### **Issue: "Invalid redirect URI"**
- Check GitHub OAuth App callback URL
- Must be exactly: `http://localhost:3000/api/auth/callback/github`

### **Issue: "Client ID not found"**
- Verify environment variables are set
- Restart development server after changes
- Check `.env.local` file exists in project root

### **Issue: Still getting errors**
- Check browser console for specific error messages
- Verify all environment variables are set correctly
- Ensure GitHub OAuth App is active (not suspended)

## ✅ **Success Indicators**

- ✅ No authentication errors in console
- ✅ GitHub OAuth page loads correctly
- ✅ After authorization, redirects to dashboard
- ✅ User session is established
- ✅ Dashboard loads with user information

## 🚀 **Expected Flow**

1. **Click Login** → Redirect to GitHub OAuth
2. **GitHub Authorization** → User authorizes app
3. **Callback to NextAuth** → `http://localhost:3000/api/auth/callback/github`
4. **Session Created** → User data stored
5. **Redirect to Dashboard** → `http://localhost:3000/dashboard`

The authentication should now work perfectly! 🎉

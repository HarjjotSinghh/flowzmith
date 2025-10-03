# GitHub OAuth Setup Guide

## 1. Create GitHub OAuth App

1. Go to [GitHub Developer Settings](https://github.com/settings/developers)
2. Click "New OAuth App"
3. Fill in the following details:
   - **Application name**: `Flow Builder Dashboard`
   - **Homepage URL**: `http://localhost:3000` (for development)
   - **Authorization callback URL**: `http://localhost:3000/api/auth/callback/github`

## 2. Get Credentials

After creating the OAuth app, you'll get:
- **Client ID**: Copy this value
- **Client Secret**: Click "Generate a new client secret" and copy the value

## 3. Environment Variables

Create a `.env.local` file in your project root with:

```env
# NextAuth.js Configuration
NEXTAUTH_URL=http://localhost:3000
NEXTAUTH_SECRET=your-secret-key-here

# GitHub OAuth Configuration
GITHUB_CLIENT_ID=your-github-client-id
GITHUB_CLIENT_SECRET=your-github-client-secret

# Optional: Database (if using database sessions)
# DATABASE_URL=your-database-url
```

## 4. Generate NextAuth Secret

Run this command to generate a secure secret:

```bash
openssl rand -base64 32
```

Or use an online generator: https://generate-secret.vercel.app/32

## 5. Production Setup

For production deployment:

1. Update GitHub OAuth App settings:
   - **Homepage URL**: `https://yourdomain.com`
   - **Authorization callback URL**: `https://yourdomain.com/api/auth/callback/github`

2. Update environment variables:
   ```env
   NEXTAUTH_URL=https://yourdomain.com
   NEXTAUTH_SECRET=your-production-secret
   GITHUB_CLIENT_ID=your-github-client-id
   GITHUB_CLIENT_SECRET=your-github-client-secret
   ```

## 6. Testing

1. Start your development server:
   ```bash
   npm run dev
   ```

2. Navigate to `http://localhost:3000/login`
3. Click "Continue with GitHub"
4. You should be redirected to the dashboard after successful authentication

## Troubleshooting

### Common Issues:

1. **"Invalid redirect URI"**: Make sure the callback URL in GitHub matches exactly
2. **"Client ID not found"**: Check your environment variables are loaded correctly
3. **"Secret mismatch"**: Verify the client secret is correct and not expired

### Debug Steps:

1. Check console for error messages
2. Verify environment variables are loaded: `console.log(process.env.GITHUB_CLIENT_ID)`
3. Check GitHub OAuth app settings match your URLs
4. Ensure NEXTAUTH_SECRET is set and secure

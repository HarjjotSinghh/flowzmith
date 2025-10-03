# Database Setup Guide

## 🗄️ **Drizzle PostgreSQL Configuration**

I've set up a complete Drizzle ORM configuration with PostgreSQL for storing user variables and related data.

## 📁 **Files Created**

### **Database Schema** (`lib/db/schema.ts`)
- **Users Table**: Store user information from GitHub OAuth
- **User Variables Table**: Store user-specific variables and settings
- **User Preferences**: Theme, language, timezone, notifications
- **User Sessions**: Track active user sessions
- **User Activity**: Log user actions and activities
- **User API Keys**: Manage API keys for external integrations

### **Database Connection** (`lib/db/index.ts`)
- PostgreSQL connection with connection pooling
- Database utility functions for testing and stats
- Type-safe database operations

### **Query Functions** (`lib/db/queries.ts`)
- Complete CRUD operations for all tables
- User management functions
- Variable management with upsert functionality
- Session and activity tracking
- API key management

### **Migration Files** (`lib/db/migrations/`)
- Initial database schema migration
- Proper foreign key constraints
- Performance indexes

## 🔧 **Environment Variables Required**

Add these to your `.env.local` file:

```bash
# Database Configuration
DATABASE_URL="postgresql://username:password@localhost:5432/flow_builder_db"

# NextAuth Configuration (existing)
NEXTAUTH_URL="http://localhost:3000"
NEXTAUTH_SECRET="your-secret-key-here"

# GitHub OAuth (existing)
GITHUB_CLIENT_ID="your-github-client-id"
GITHUB_CLIENT_SECRET="your-github-client-secret"

# AI Configuration (existing)
GROQ_API_KEY="your-groq-api-key"
```

## 🚀 **Setup Instructions**

### **1. Install PostgreSQL**
```bash
# On Windows (using Chocolatey)
choco install postgresql

# On macOS (using Homebrew)
brew install postgresql

# On Ubuntu/Debian
sudo apt-get install postgresql postgresql-contrib
```

### **2. Create Database**
```bash
# Connect to PostgreSQL
psql -U postgres

# Create database
CREATE DATABASE flow_builder_db;

# Create user (optional)
CREATE USER flow_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE flow_builder_db TO flow_user;
```

### **3. Run Migrations**
```bash
# Generate migration
npx drizzle-kit generate

# Push to database
npx drizzle-kit push

# Or run migrations manually
npx drizzle-kit migrate
```

### **4. Test Database Connection**
```bash
# Test connection
npm run db:test
```

## 📊 **Database Schema Overview**

### **Users Table**
```sql
- id (uuid, primary key)
- email (text, unique)
- name (text)
- image (text)
- github_id (text, unique)
- created_at, updated_at (timestamps)
```

### **User Variables Table**
```sql
- id (uuid, primary key)
- user_id (uuid, foreign key)
- key (varchar, variable name)
- value (text, string value)
- json_value (jsonb, complex data)
- type (varchar, data type)
- description (text)
- is_public (boolean)
- created_at, updated_at (timestamps)
```

### **User Preferences Table**
```sql
- id (uuid, primary key)
- user_id (uuid, foreign key)
- theme (varchar, light/dark/system)
- language (varchar, language code)
- timezone (varchar, timezone)
- notifications (jsonb, notification settings)
- created_at, updated_at (timestamps)
```

## 🔍 **Usage Examples**

### **Store User Variables**
```typescript
import { userVariableQueries } from '@/lib/db/queries'

// Store a simple string variable
await userVariableQueries.upsert(
  userId, 
  'api_key', 
  'secret-key-123', 
  'string', 
  'User API key for external service'
)

// Store JSON data
await userVariableQueries.create({
  userId,
  key: 'preferences',
  jsonValue: { theme: 'dark', notifications: true },
  type: 'json',
  description: 'User preferences'
})
```

### **Get User Variables**
```typescript
// Get all variables for a user
const variables = await userVariableQueries.getByUserId(userId)

// Get specific variable
const apiKey = await userVariableQueries.getByKey(userId, 'api_key')
```

### **User Management**
```typescript
import { userQueries } from '@/lib/db/queries'

// Create user after GitHub OAuth
const user = await userQueries.create({
  email: 'user@example.com',
  name: 'John Doe',
  githubId: '12345'
})

// Update user
await userQueries.update(userId, { name: 'New Name' })
```

## 🛠️ **Available Scripts**

Add these to your `package.json`:

```json
{
  "scripts": {
    "db:generate": "drizzle-kit generate",
    "db:push": "drizzle-kit push",
    "db:migrate": "drizzle-kit migrate",
    "db:studio": "drizzle-kit studio",
    "db:test": "node -e \"import('./lib/db/index.js').then(m => m.dbUtils.testConnection()).then(console.log)\""
  }
}
```

## 🔒 **Security Features**

- **Foreign Key Constraints**: Proper referential integrity
- **Cascade Deletes**: User deletion removes all related data
- **Indexed Queries**: Optimized database performance
- **Type Safety**: Full TypeScript support
- **Connection Pooling**: Efficient database connections

## 📈 **Performance Optimizations**

- **Database Indexes**: On frequently queried columns
- **Connection Pooling**: Reuse database connections
- **Query Optimization**: Efficient Drizzle ORM queries
- **Lazy Loading**: Load data only when needed

## 🎯 **Next Steps**

1. **Set up PostgreSQL database**
2. **Add environment variables**
3. **Run database migrations**
4. **Test database connection**
5. **Integrate with authentication system**

The database is now ready to store user variables, preferences, and all related data! 🎉

# 🗄️ **Updated Database Schema - Chat Tracking & User Management**

## ✅ **Enhanced Database Schema for Project Requirements**

I've updated the database schema to support comprehensive chat request tracking, user plan management, and dashboard analytics based on your project requirements.

## 📊 **Updated Schema Overview**

### **🔧 Enhanced Users Table**
```sql
- id (uuid, primary key)
- email (text, unique) ⭐ - Primary identifier for auth
- name (text)
- image (text)
- github_id (text, unique)
- plan (varchar) - free, pro, enterprise
- plan_expires_at (timestamp)
- requests_used (integer) - Current month usage
- requests_limit (integer) - Monthly limit
- is_active (boolean) - Account status
- last_login_at (timestamp)
- created_at, updated_at (timestamps)
```

### **💬 New Chat Requests Table**
```sql
- id (uuid, primary key)
- user_id (uuid, foreign key)
- session_id (text) - Group related requests
- prompt (text) - User input
- response (text) - AI response
- model (varchar) - AI model used
- tokens_used (integer) - Token consumption
- cost (integer) - Cost in cents
- duration (integer) - Response time in ms
- status (varchar) - pending, completed, failed
- error_message (text)
- ip_address (text)
- user_agent (text)
- started_at, completed_at, created_at (timestamps)
```

### **📋 User Plans Table**
```sql
- id (uuid, primary key)
- user_id (uuid, foreign key)
- plan_name (varchar) - free, pro, enterprise
- monthly_requests (integer) - Monthly limit
- daily_requests (integer) - Daily limit
- max_tokens_per_request (integer) - Token limit
- features (jsonb) - Plan features array
- is_active (boolean) - Current plan status
- price_per_month (integer) - Cost in cents
- billing_cycle (varchar) - monthly, yearly
- starts_at, expires_at (timestamps)
- created_at, updated_at (timestamps)
```

### **📈 Request Analytics Table**
```sql
- id (uuid, primary key)
- user_id (uuid, foreign key)
- request_id (uuid, foreign key to chat_requests)
- request_type (varchar) - chat, code_generation, analysis
- category (varchar) - nft, token, marketplace, etc.
- complexity (varchar) - low, medium, high
- response_time (integer) - Milliseconds
- tokens_input (integer) - Input tokens
- tokens_output (integer) - Output tokens
- user_rating (integer) - 1-5 rating
- was_successful (boolean)
- created_at (timestamp)
```

### **📊 User Dashboard Data Table**
```sql
- id (uuid, primary key)
- user_id (uuid, foreign key)
- total_requests (integer) - All-time requests
- total_tokens_used (integer) - All-time tokens
- total_cost (integer) - All-time cost
- average_response_time (integer) - Average response time
- requests_by_category (jsonb) - Usage by category
- requests_this_month (integer) - Monthly usage
- requests_today (integer) - Daily usage
- last_calculated_at (timestamp)
- created_at, updated_at (timestamps)
```

## 🔄 **Chat Request Tracking Flow**

### **1. Request Initiation**
```typescript
// POST /api/chat/track
{
  "prompt": "Create an NFT contract",
  "sessionId": "session-123",
  "model": "gpt-4",
  "requestType": "code_generation",
  "category": "nft",
  "complexity": "high"
}
```

### **2. Request Completion**
```typescript
// PUT /api/chat/track
{
  "requestId": "req-123",
  "status": "completed",
  "response": "Generated contract code...",
  "tokensUsed": 1500,
  "cost": 3,
  "duration": 2500,
  "userRating": 5
}
```

### **3. Analytics Recording**
- Automatic analytics record creation
- Performance metrics tracking
- User rating collection
- Category-based usage analysis

## 📊 **Dashboard Data API**

### **GET /api/user/dashboard**
Returns comprehensive dashboard data:
```json
{
  "user": {
    "id": "user-123",
    "email": "user@example.com",
    "plan": "pro",
    "requestsUsed": 45,
    "requestsLimit": 1000
  },
  "metrics": {
    "totalRequests": 1250,
    "totalTokensUsed": 45000,
    "totalCost": 125,
    "averageResponseTime": 1800,
    "requestsThisMonth": 45,
    "requestsToday": 3
  },
  "limits": {
    "monthlyUsed": 45,
    "monthlyLimit": 1000,
    "dailyUsed": 3,
    "dailyLimit": 50,
    "canMakeRequest": true,
    "planName": "pro"
  },
  "performance": {
    "averageResponseTime": 1800,
    "successRate": 0.95,
    "averageRating": 4.2,
    "totalRequests": 1250
  },
  "recentRequests": [...],
  "requestsByCategory": {
    "nft": 15,
    "token": 12,
    "marketplace": 8
  }
}
```

## 🚀 **Key Features**

### **📈 Request Tracking**
- **Complete Timeline**: Track every chat request from start to finish
- **Session Grouping**: Group related requests in sessions
- **Performance Metrics**: Response time, token usage, cost tracking
- **Error Handling**: Track failed requests and error messages

### **👤 User Plan Management**
- **Plan Limits**: Monthly and daily request limits
- **Feature Access**: Plan-based feature restrictions
- **Usage Tracking**: Real-time usage monitoring
- **Upgrade/Downgrade**: Plan change management

### **📊 Analytics & Insights**
- **Usage Analytics**: Detailed usage patterns
- **Performance Metrics**: Response time and success rates
- **Category Analysis**: Usage by request type
- **User Ratings**: Quality feedback tracking

### **🎯 Dashboard Integration**
- **Real-time Metrics**: Live dashboard data
- **Usage Visualization**: Charts and graphs
- **Plan Status**: Current plan and limits
- **Performance Insights**: Success rates and ratings

## 🔧 **API Endpoints**

### **Chat Tracking**
- `POST /api/chat/track` - Start tracking a request
- `PUT /api/chat/track` - Update request status and metrics

### **Dashboard Data**
- `GET /api/user/dashboard` - Get dashboard metrics
- `POST /api/user/dashboard` - Recalculate dashboard data

### **User Management**
- `GET /api/user/variables` - Get user variables
- `POST /api/user/variables` - Create/update variables
- `PUT /api/user/variables` - Bulk update variables

## 🗃️ **Database Migrations**

### **Migration 1: Initial Schema**
- Users, variables, preferences, sessions, activity, API keys

### **Migration 2: Chat Tracking** ⭐
- Enhanced users table with plan fields
- Chat requests table for request tracking
- User plans table for subscription management
- Request analytics for detailed metrics
- Dashboard data table for cached metrics

## 🎯 **Usage Examples**

### **Track Chat Request**
```typescript
// Start tracking
const response = await fetch('/api/chat/track', {
  method: 'POST',
  body: JSON.stringify({
    prompt: 'Create an NFT contract',
    sessionId: 'session-123',
    category: 'nft',
    complexity: 'high'
  })
})

// Update on completion
await fetch('/api/chat/track', {
  method: 'PUT',
  body: JSON.stringify({
    requestId: 'req-123',
    status: 'completed',
    tokensUsed: 1500,
    cost: 3,
    duration: 2500,
    userRating: 5
  })
})
```

### **Get Dashboard Data**
```typescript
const dashboard = await fetch('/api/user/dashboard')
const data = await dashboard.json()

console.log('Total requests:', data.dashboard.metrics.totalRequests)
console.log('Monthly usage:', data.dashboard.limits.monthlyUsed)
console.log('Can make request:', data.dashboard.limits.canMakeRequest)
```

## ✅ **Ready for Production**

The updated schema now provides:

- ✅ **Complete Request Tracking**: Every chat interaction is tracked
- ✅ **User Plan Management**: Subscription and limit management
- ✅ **Dashboard Analytics**: Comprehensive usage insights
- ✅ **Performance Monitoring**: Response times and success rates
- ✅ **Category Analysis**: Usage patterns by request type
- ✅ **Real-time Limits**: Live usage monitoring
- ✅ **Email-based Auth**: Email as unique identifier
- ✅ **Timeline Tracking**: Complete request history

The database is now fully equipped to support your Flow Builder application with comprehensive chat tracking, user management, and analytics! 🎉

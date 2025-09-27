# Dashboard Dynamic Setup Guide

This guide explains how to set up the dynamic dashboard with database integration.

## Overview

The dashboard now fetches real-time data from the database and displays:
- **Usage Statistics**: API calls, tokens processed, response times, success rates
- **Cost Tracking**: Real-time cost breakdown and budget monitoring
- **Recent Activity**: Live activity feed from user interactions
- **Analytics**: Performance metrics and usage patterns

## Database Setup

### 1. Environment Variables

Add these to your `.env.local` file:

```env
# Database Configuration
DATABASE_URL=postgresql://username:password@localhost:5432/ai_landing_page

# Optional: Database connection pool settings
DB_POOL_SIZE=10
DB_POOL_TIMEOUT=30000
```

### 2. Database Schema

The dashboard uses the following tables from `lib/db/schema.ts`:

- **`users`**: User information and limits
- **`chatRequests`**: All AI chat interactions
- **`userActivity`**: User activity logs
- **`requestAnalytics`**: Detailed request analytics
- **`userDashboardData`**: Cached dashboard metrics

### 3. Database Migration

Run the database migrations to create the tables:

```bash
# If using Drizzle migrations
npx drizzle-kit push

# Or run the SQL directly
psql -d ai_landing_page -f lib/db/migrations/001_initial_schema.sql
```

## API Routes

### 1. Dashboard Stats (`/api/dashboard/stats`)

**GET** - Fetches usage statistics and recent activity

**Response:**
```json
{
  "apiCallsToday": {
    "value": "42",
    "change": "+12.5%",
    "trend": "up"
  },
  "tokensProcessed": {
    "value": "1.2K",
    "change": "+8.3%",
    "trend": "up"
  },
  "avgResponseTime": {
    "value": "1.2s",
    "change": "-15.2%",
    "trend": "up"
  },
  "successRate": {
    "value": "99.8%",
    "change": "+0.1%",
    "trend": "up"
  },
  "totalRequests": 150,
  "weekRequests": 45,
  "monthRequests": 120,
  "recentActivity": [...]
}
```

### 2. Cost Tracking (`/api/dashboard/costs`)

**GET** - Fetches cost breakdown and budget information

**Response:**
```json
{
  "totalCost": "0.0047",
  "projectedMonthlyCost": "0.0141",
  "remainingCredits": 850,
  "costBreakdown": {
    "apiCalls": { "count": 42, "cost": 0.0042, "percentage": 70 },
    "storage": { "count": 5, "cost": 0.0005, "percentage": 20 },
    "processing": { "count": 2, "cost": 0.0002, "percentage": 10 }
  },
  "costTrend": "up",
  "savings": {
    "thisMonth": "2.50",
    "comparedToLastMonth": "up"
  }
}
```

### 3. Analytics (`/api/dashboard/analytics`)

**GET** - Fetches detailed analytics and performance metrics

**Response:**
```json
{
  "timeline": [...],
  "weeklyStats": { "total": 45, "completed": 42, "failed": 3 },
  "monthlyStats": { "total": 120, "completed": 115, "failed": 5 },
  "performance": {
    "avgResponseTime": 1.2,
    "successRate": 99.5,
    "uptime": 99.9,
    "errorRate": 0.1
  },
  "patterns": {
    "peakHours": [9, 10, 11, 14, 15, 16],
    "mostActiveDay": "Tuesday",
    "avgSessionLength": 15.5,
    "requestsPerSession": 3.2
  }
}
```

### 4. Analytics Store (`/api/dashboard/analytics/store`)

**POST** - Stores analytics events

**Request:**
```json
{
  "eventType": "api_call",
  "eventData": { "endpoint": "/api/generate", "method": "POST" },
  "timestamp": "2024-01-15T10:30:00Z",
  "metadata": { "source": "dashboard" }
}
```

**GET** - Retrieves analytics events with filtering

**Query Parameters:**
- `eventType`: Filter by event type
- `startDate`: Start date filter
- `endDate`: End date filter
- `limit`: Number of events to return

## Components

### 1. UsageStats Component

- **Fetches**: Real-time usage statistics
- **Updates**: Every 30 seconds (configurable)
- **Features**: Loading states, error handling, trend indicators

### 2. CostTracking Component

- **Fetches**: Cost breakdown and budget information
- **Updates**: Real-time cost calculations
- **Features**: Budget progress bars, cost breakdown charts

### 3. RecentActivity Component

- **Fetches**: Recent user activity from chat requests
- **Updates**: Live activity feed
- **Features**: Activity categorization, time formatting, error detection

## Error Handling

### 1. Database Unavailable

If the database is not available, the API routes return mock data:

```json
{
  "apiCallsToday": { "value": "0", "change": "0%", "trend": "neutral" },
  "tokensProcessed": { "value": "0K", "change": "0%", "trend": "neutral" },
  "avgResponseTime": { "value": "1.2s", "change": "0%", "trend": "neutral" },
  "successRate": { "value": "99.9%", "change": "0%", "trend": "up" }
}
```

### 2. Component Error States

Components display error messages when API calls fail:

```jsx
{error && (
  <div className="bg-red-500/10 border border-red-500/20 rounded-lg p-4">
    <p className="text-red-400 text-sm">Failed to load data: {error}</p>
  </div>
)}
```

### 3. Loading States

All components show loading indicators while fetching data:

```jsx
{loading ? (
  <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
) : (
  // Component content
)}
```

## Performance

### 1. Caching

- Dashboard data is cached for 30 seconds
- Database queries are optimized with proper indexing
- Components use React.memo for performance

### 2. Real-time Updates

- Components automatically refresh data
- WebSocket integration for live updates (optional)
- Background data fetching

### 3. Database Optimization

- Proper indexing on frequently queried columns
- Connection pooling for database efficiency
- Query optimization for large datasets

## Security

### 1. Authentication

- All API routes require authentication
- User data is isolated by user ID
- Session validation on every request

### 2. Data Privacy

- No sensitive data exposed to client
- Proper error handling to prevent data leaks
- Input validation and sanitization

## Monitoring

### 1. Logging

- All API calls are logged
- Error tracking and monitoring
- Performance metrics collection

### 2. Health Checks

- Database connection health checks
- API endpoint monitoring
- Component error tracking

## Troubleshooting

### 1. Common Issues

**Database Connection Failed:**
- Check DATABASE_URL environment variable
- Verify database server is running
- Check network connectivity

**API Routes Not Working:**
- Verify authentication is working
- Check database schema is up to date
- Review error logs in console

**Components Not Loading:**
- Check network requests in browser dev tools
- Verify API routes are accessible
- Check for JavaScript errors

### 2. Debug Mode

Enable debug logging:

```javascript
localStorage.setItem('debug', 'dashboard:*')
```

### 3. Database Queries

Test database queries directly:

```sql
-- Check user data
SELECT * FROM users WHERE email = 'user@example.com';

-- Check chat requests
SELECT COUNT(*) FROM chat_requests WHERE user_id = 'user-id';

-- Check recent activity
SELECT * FROM chat_requests 
WHERE user_id = 'user-id' 
ORDER BY started_at DESC 
LIMIT 10;
```

## Future Enhancements

### 1. Real-time Updates

- WebSocket integration for live data
- Server-sent events for real-time updates
- Push notifications for important events

### 2. Advanced Analytics

- Machine learning insights
- Predictive analytics
- Advanced reporting features

### 3. Customization

- User-configurable dashboard widgets
- Custom metrics and KPIs
- Personalized dashboard layouts

---

*This dashboard provides a comprehensive view of your AI development activity with real-time data and analytics.*

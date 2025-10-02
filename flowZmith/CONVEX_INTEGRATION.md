# Convex Integration Documentation

## Overview

This document outlines the complete integration of Convex into the Flowzmith application, providing real-time database functionality, collaboration features, and live analytics.

## 🚀 Features Implemented

### 1. Real-time Database with Convex
- **Smart Contract Management**: Create, read, update, and delete smart contracts
- **User Management**: User profiles and authentication integration
- **Collaboration Sessions**: Real-time collaborative editing sessions
- **Deployment Tracking**: Monitor smart contract deployments across networks
- **Notifications System**: Real-time notifications for deployments and collaboration
- **Analytics Dashboard**: Live metrics and deployment statistics

### 2. Database Schema

The Convex schema includes the following tables:

#### Users Table
```typescript
users: defineTable({
  clerkId: v.string(),
  email: v.string(),
  name: v.string(),
  avatar: v.optional(v.string()),
  createdAt: v.number(),
  lastActive: v.number(),
})
```

#### Smart Contracts Table
```typescript
contracts: defineTable({
  name: v.string(),
  description: v.string(),
  code: v.string(),
  language: v.string(),
  network: v.string(),
  status: v.string(),
  userId: v.string(),
  isPublic: v.boolean(),
  collaborators: v.array(v.string()),
  tags: v.array(v.string()),
})
```

#### Collaboration Sessions Table
```typescript
collaborationSessions: defineTable({
  contractId: v.id("contracts"),
  participants: v.array(v.object({
    userId: v.string(),
    userName: v.string(),
    userAvatar: v.string(),
    joinedAt: v.number(),
    role: v.string(),
  })),
  isActive: v.boolean(),
  lastActivity: v.number(),
})
```

#### Deployments Table
```typescript
deployments: defineTable({
  contractId: v.id("contracts"),
  userId: v.string(),
  network: v.string(),
  status: v.string(),
  transactionHash: v.optional(v.string()),
  contractAddress: v.optional(v.string()),
  gasUsed: v.optional(v.number()),
  deploymentCost: v.optional(v.string()),
  errorMessage: v.optional(v.string()),
})
```

#### Notifications Table
```typescript
notifications: defineTable({
  userId: v.string(),
  type: v.string(),
  title: v.string(),
  message: v.string(),
  read: v.boolean(),
  metadata: v.optional(v.object({
    contractId: v.optional(v.id("contracts")),
    deploymentId: v.optional(v.id("deployments")),
    sessionId: v.optional(v.id("collaborationSessions")),
  })),
})
```

### 3. Convex Functions

#### Contract Management Functions
- `createContract`: Create new smart contracts
- `getUserContracts`: Get user's contracts with filtering
- `getPublicContracts`: Get public contracts
- `getContract`: Get specific contract details
- `updateContract`: Update contract code and metadata
- `addCollaborator`: Add collaborators to contracts
- `searchContracts`: Search contracts by name/description
- `deleteContract`: Delete contracts
- `getContractAnalytics`: Get contract usage analytics

#### Collaboration Functions
- `startCollaborationSession`: Start new collaboration session
- `joinCollaborationSession`: Join existing session
- `leaveCollaborationSession`: Leave session
- `updateCursorPosition`: Update user cursor position
- `applyCodeChange`: Apply real-time code changes
- `getActiveSession`: Get active session for contract
- `getRecentChanges`: Get recent code changes
- `cleanupInactiveSessions`: Clean up inactive sessions
- `getCollaborationStats`: Get collaboration statistics

#### Deployment Functions
- `startDeployment`: Initiate contract deployment
- `updateDeploymentStatus`: Update deployment status
- `getDeployment`: Get deployment details
- `getContractDeployments`: Get deployments for contract
- `getUserDeployments`: Get user's deployments
- `getDeploymentStats`: Get deployment statistics
- `getRecentDeploymentActivity`: Get recent deployment activity
- `cancelDeployment`: Cancel pending deployment

#### Notification Functions
- `getUserNotifications`: Get user notifications
- `markNotificationAsRead`: Mark notification as read
- `markAllNotificationsAsRead`: Mark all notifications as read
- `createNotification`: Create new notification
- `deleteNotification`: Delete notification
- `getUnreadNotificationCount`: Get unread count
- `cleanupOldNotifications`: Clean up old notifications
- `sendSystemNotification`: Send system-wide notifications

### 4. React Hooks

Custom hooks are provided for easy integration:

#### Contract Hooks (`/hooks/use-convex-contracts.ts`)
- `useUserContracts()`: Get user's contracts
- `usePublicContracts()`: Get public contracts
- `useContract(id)`: Get specific contract
- `useCreateContract()`: Create contract mutation
- `useUpdateContract()`: Update contract mutation
- `useAddCollaborator()`: Add collaborator mutation
- `useSearchContracts(query)`: Search contracts
- `useDeleteContract()`: Delete contract mutation
- `useContractAnalytics(contractId)`: Get contract analytics

#### Deployment Hooks (`/hooks/use-convex-deployments.ts`)
- `useStartDeployment()`: Start deployment mutation
- `useUpdateDeploymentStatus()`: Update deployment status
- `useDeployment(id)`: Get deployment details
- `useContractDeployments(contractId)`: Get contract deployments
- `useUserDeployments()`: Get user deployments
- `useDeploymentStats()`: Get deployment statistics
- `useRecentDeploymentActivity()`: Get recent activity
- `useCancelDeployment()`: Cancel deployment mutation

#### Collaboration Hooks (`/hooks/use-convex-collaboration.ts`)
- `useStartCollaborationSession()`: Start session mutation
- `useJoinCollaborationSession()`: Join session mutation
- `useLeaveCollaborationSession()`: Leave session mutation
- `useUpdateCursorPosition()`: Update cursor mutation
- `useApplyCodeChange()`: Apply code change mutation
- `useActiveSession(contractId)`: Get active session
- `useRecentChanges(sessionId)`: Get recent changes
- `useCollaborationStats(contractId)`: Get collaboration stats

#### Notification Hooks (`/hooks/use-convex-notifications.ts`)
- `useUserNotifications()`: Get user notifications
- `useMarkNotificationAsRead()`: Mark as read mutation
- `useMarkAllNotificationsAsRead()`: Mark all as read mutation
- `useCreateNotification()`: Create notification mutation
- `useDeleteNotification()`: Delete notification mutation
- `useUnreadNotificationCount()`: Get unread count
- `useSendSystemNotification()`: Send system notification

### 5. UI Components

#### Real-time Analytics Dashboard (`/components/analytics/real-time-dashboard.tsx`)
- Live deployment metrics
- Contract statistics
- Success rate tracking
- Recent activity feed
- Performance indicators

#### Real-time Notifications (`/components/notifications/real-time-notifications.tsx`)
- Live notification feed
- Mark as read functionality
- Notification filtering
- Real-time updates
- Notification management

#### Real-time Collaboration (`/components/collaboration/real-time-collaboration.tsx`)
- Active session management
- Participant tracking
- Real-time code changes
- Cursor position sharing
- Collaboration statistics

### 6. Environment Configuration

#### Development Environment
```env
CONVEX_DEPLOYMENT=dev:your-deployment-id
NEXT_PUBLIC_CONVEX_URL=https://your-deployment.convex.cloud
```

#### Production Environment
```env
# CONVEX_DEPLOYMENT=prod:your-production-deployment-id
# NEXT_PUBLIC_CONVEX_URL=https://your-production-deployment.convex.cloud
```

### 7. Authentication Integration

The integration supports both Clerk and simple authentication:

#### With Clerk (Recommended)
```typescript
import { ConvexProviderWithClerk } from "convex/react-clerk";
import { ClerkProvider, useAuth } from "@clerk/nextjs";

export function ConvexProvider({ children }: { children: React.ReactNode }) {
  return (
    <ClerkProvider>
      <ConvexProviderWithClerk client={convex} useAuth={useAuth}>
        {children}
      </ConvexProviderWithClerk>
    </ClerkProvider>
  );
}
```

#### Simple Provider (Without Clerk)
```typescript
import { ConvexReactClient } from "convex/react";

export function SimpleConvexProvider({ children }: { children: React.ReactNode }) {
  return (
    <ConvexReactClient client={convex}>
      {children}
    </ConvexReactClient>
  );
}
```

## 🛠️ Setup Instructions

### 1. Install Dependencies
```bash
npm install convex @clerk/nextjs
```

### 2. Initialize Convex
```bash
npx convex dev --configure
```

### 3. Deploy Schema and Functions
```bash
npx convex dev
```

### 4. Update Environment Variables
Add the Convex deployment URL and deployment ID to your `.env.local` file.

### 5. Wrap Your App
Update your root layout to include the Convex provider:

```typescript
import { ConvexProvider } from '@/components/providers/convex-provider';

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <ConvexProvider>
          {children}
        </ConvexProvider>
      </body>
    </html>
  );
}
```

## 🧪 Testing

### Test Page
A comprehensive test page is available at `/convex-test` that demonstrates:
- Real-time dashboard functionality
- Notification system
- Collaboration features
- Contract management
- Integration status

### Running Tests
1. Start the Next.js development server: `npm run dev`
2. Start the Convex development server: `npx convex dev`
3. Navigate to `http://localhost:3001/convex-test`
4. Test the various features using the provided buttons

## 📊 Real-time Features

### 1. Live Data Updates
All data automatically updates in real-time across all connected clients without manual refresh.

### 2. Collaborative Editing
Multiple users can collaborate on smart contracts with:
- Real-time cursor tracking
- Live code changes
- Participant awareness
- Change history

### 3. Deployment Monitoring
Track deployment progress with:
- Real-time status updates
- Success/failure notifications
- Gas usage tracking
- Network monitoring

### 4. Analytics Dashboard
Monitor application usage with:
- Live deployment metrics
- User activity tracking
- Performance indicators
- Success rate monitoring

## 🔧 Customization

### Adding New Tables
1. Update the schema in `convex/schema.ts`
2. Create corresponding functions in `convex/`
3. Generate types with `npx convex dev`
4. Create React hooks in `hooks/`
5. Build UI components in `components/`

### Extending Functions
1. Add new functions to existing files in `convex/`
2. Update corresponding hooks
3. Implement UI components
4. Test functionality

## 🚀 Production Deployment

### 1. Production Environment
1. Create a production deployment in Convex dashboard
2. Update environment variables for production
3. Deploy your Next.js application
4. Ensure Convex functions are deployed to production

### 2. Environment Variables
Make sure to set the production Convex environment variables:
```env
CONVEX_DEPLOYMENT=prod:your-production-deployment-id
NEXT_PUBLIC_CONVEX_URL=https://your-production-deployment.convex.cloud
```

## 📝 Notes

- All Convex functions include proper authentication and authorization
- Real-time updates work automatically without additional configuration
- The integration is fully typed with TypeScript
- Error handling is implemented throughout the application
- The system is designed to scale with your application needs

## 🔗 Resources

- [Convex Documentation](https://docs.convex.dev/)
- [Convex React Integration](https://docs.convex.dev/client/react)
- [Clerk Authentication](https://clerk.com/docs)
- [Next.js Documentation](https://nextjs.org/docs)

This integration provides a solid foundation for real-time smart contract collaboration and management in the Flowzmith application.
import { db, dbUtils } from './index'
import { userQueries, userVariableQueries, userPreferenceQueries } from './queries'

// Utility functions for common database operations
export const dbHelpers = {
  // Initialize user data after OAuth login
  async initializeUser(userData: {
    email: string
    name?: string
    image?: string
    githubId?: string
  }) {
    try {
      // Check if user exists
      let user = await userQueries.findByEmail(userData.email)
      
      if (!user) {
        // Create new user
        user = await userQueries.create({
          email: userData.email,
          name: userData.name,
          image: userData.image,
          githubId: userData.githubId
        })
      } else {
        // Update existing user with latest data
        user = await userQueries.update(user.id, {
          name: userData.name,
          image: userData.image,
          githubId: userData.githubId
        })
      }

      // Initialize default preferences
      await userPreferenceQueries.upsert(user.id, {
        theme: 'system',
        language: 'en',
        timezone: 'UTC',
        notifications: {}
      })

      // Set default user variables
      await userVariableQueries.upsert(user.id, 'welcome_completed', 'false', 'boolean', 'Has user completed welcome flow')
      await userVariableQueries.upsert(user.id, 'onboarding_step', '0', 'number', 'Current onboarding step')
      await userVariableQueries.upsert(user.id, 'dashboard_layout', 'default', 'string', 'Dashboard layout preference')

      return user
    } catch (error) {
      console.error('Error initializing user:', error)
      throw error
    }
  },

  // Get user dashboard data
  async getUserDashboardData(userId: string) {
    try {
      const [user, variables, preferences] = await Promise.all([
        userQueries.findById(userId),
        userVariableQueries.getByUserId(userId),
        userPreferenceQueries.getByUserId(userId)
      ])

      return {
        user,
        variables: variables.reduce((acc, variable) => {
          acc[variable.key] = {
            value: variable.value,
            jsonValue: variable.jsonValue,
            type: variable.type,
            description: variable.description,
            isPublic: variable.isPublic
          }
          return acc
        }, {} as Record<string, any>),
        preferences
      }
    } catch (error) {
      console.error('Error getting user dashboard data:', error)
      throw error
    }
  },

  // Update user variable with type safety
  async updateUserVariable(userId: string, key: string, value: any, type: string = 'string', description?: string) {
    try {
      // Validate value based on type
      let processedValue = value
      let jsonValue = null

      switch (type) {
        case 'number':
          processedValue = String(Number(value))
          break
        case 'boolean':
          processedValue = String(Boolean(value))
          break
        case 'json':
          jsonValue = typeof value === 'string' ? JSON.parse(value) : value
          processedValue = null
          break
        default:
          processedValue = String(value)
      }

      return await userVariableQueries.upsert(userId, key, processedValue, type, description)
    } catch (error) {
      console.error('Error updating user variable:', error)
      throw error
    }
  },

  // Get user variable with type conversion
  async getUserVariable(userId: string, key: string) {
    try {
      const variable = await userVariableQueries.getByKey(userId, key)
      if (!variable) return null

      // Convert value based on type
      let value = variable.value
      if (variable.jsonValue) {
        value = variable.jsonValue
      } else {
        switch (variable.type) {
          case 'number':
            value = Number(variable.value)
            break
          case 'boolean':
            value = variable.value === 'true'
            break
          case 'json':
            value = JSON.parse(variable.value || '{}')
            break
        }
      }

      return {
        ...variable,
        value
      }
    } catch (error) {
      console.error('Error getting user variable:', error)
      throw error
    }
  },

  // Bulk update user variables
  async bulkUpdateVariables(userId: string, variables: Record<string, { value: any, type?: string, description?: string }>) {
    try {
      const results = []
      for (const [key, data] of Object.entries(variables)) {
        const result = await this.updateUserVariable(
          userId, 
          key, 
          data.value, 
          data.type || 'string', 
          data.description
        )
        results.push(result)
      }
      return results
    } catch (error) {
      console.error('Error bulk updating variables:', error)
      throw error
    }
  },

  // Get user statistics
  async getUserStats(userId: string) {
    try {
      const [variables, preferences] = await Promise.all([
        userVariableQueries.getByUserId(userId),
        userPreferenceQueries.getByUserId(userId)
      ])

      return {
        totalVariables: variables.length,
        publicVariables: variables.filter(v => v.isPublic).length,
        hasPreferences: !!preferences,
        lastUpdated: variables.length > 0 ? Math.max(...variables.map(v => new Date(v.updatedAt).getTime())) : null
      }
    } catch (error) {
      console.error('Error getting user stats:', error)
      throw error
    }
  },

  // Clean up old data
  async cleanupUserData(userId: string, olderThanDays: number = 90) {
    try {
      const cutoffDate = new Date()
      cutoffDate.setDate(cutoffDate.getDate() - olderThanDays)

      // This would require additional queries for activity cleanup
      // Implementation depends on your specific cleanup needs
      console.log(`Cleanup for user ${userId} older than ${olderThanDays} days`)
    } catch (error) {
      console.error('Error cleaning up user data:', error)
      throw error
    }
  }
}

// Database health check
export const healthCheck = {
  async checkDatabase() {
    try {
      const result = await dbUtils.testConnection()
      return result
    } catch (error) {
      return { success: false, message: `Database health check failed: ${error}` }
    }
  },

  async getDatabaseStats() {
    try {
      const stats = await dbUtils.getStats()
      return {
        success: true,
        stats,
        timestamp: new Date().toISOString()
      }
    } catch (error) {
      return { success: false, message: `Failed to get database stats: ${error}` }
    }
  }
}

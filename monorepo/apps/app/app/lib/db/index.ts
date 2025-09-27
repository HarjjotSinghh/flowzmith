import { drizzle } from 'drizzle-orm/postgres-js'
import postgres from 'postgres'
import * as schema from './schema'

// Database connection
const connectionString = process.env.DATABASE_URL!

if (!connectionString) {
  throw new Error('DATABASE_URL environment variable is not set')
}

// Create the connection
const client = postgres(connectionString, {
  max: 1, // Maximum number of connections
  idle_timeout: 20, // Close idle connections after 20 seconds
  connect_timeout: 10, // Connection timeout
})

// Create the database instance
export const db = drizzle(client, { schema })

// Export schema for use in other files
export * from './schema'

// Database utility functions
export const dbUtils = {
  // Test database connection
  async testConnection() {
    try {
      await client`SELECT 1`
      return { success: true, message: 'Database connection successful' }
    } catch (error) {
      return { success: false, message: `Database connection failed: ${error}` }
    }
  },

  // Close database connection
  async closeConnection() {
    await client.end()
  },

  // Get database stats
  async getStats() {
    try {
      const [userCount] = await client`SELECT COUNT(*) as count FROM users`
      const [variableCount] = await client`SELECT COUNT(*) as count FROM user_variables`
      const [sessionCount] = await client`SELECT COUNT(*) as count FROM user_sessions`
      
      return {
        users: userCount.count,
        variables: variableCount.count,
        sessions: sessionCount.count,
      }
    } catch (error) {
      console.error('Error getting database stats:', error)
      return null
    }
  }
}

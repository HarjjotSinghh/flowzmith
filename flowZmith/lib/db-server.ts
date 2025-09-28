import { drizzle } from 'drizzle-orm/postgres-js'
import postgres from 'postgres'
import * as schema from './db/schema'

// Create the connection
const connectionString = process.env.DATABASE_URL || 'postgresql://localhost:5432/ai_landing_page'
const client = postgres(connectionString)
export const db = drizzle(client, { schema })

// Export types
export type Database = typeof db
export * from './db/schema'

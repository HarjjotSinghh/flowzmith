import { NextRequest, NextResponse } from 'next/server'
import { getServerSession } from 'next-auth'
import { authOptions } from '@/lib/auth'
import { userQueries, userVariableQueries } from '@/lib/db/queries'
import { dbHelpers } from '@/lib/db/utils'

export async function GET(request: NextRequest) {
  try {
    const session = await getServerSession(authOptions)
    
    if (!session?.user?.email) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
    }

    // Get user from database
    const user = await userQueries.findByEmail(session.user.email)
    if (!user) {
      return NextResponse.json({ error: 'User not found' }, { status: 404 })
    }

    // Get user variables
    const variables = await userVariableQueries.getByUserId(user.id)
    
    // Transform variables for API response
    const transformedVariables = variables.map(variable => ({
      id: variable.id,
      key: variable.key,
      value: variable.value,
      jsonValue: variable.jsonValue,
      type: variable.type,
      description: variable.description,
      isPublic: variable.isPublic,
      createdAt: variable.createdAt?.toISOString(),
      updatedAt: variable.updatedAt?.toISOString()
    }))

    return NextResponse.json({
      success: true,
      variables: transformedVariables
    })
  } catch (error) {
    console.error('Error getting user variables:', error)
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    )
  }
}

export async function POST(request: NextRequest) {
  try {
    const session = await getServerSession(authOptions)
    
    if (!session?.user?.email) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
    }

    const body = await request.json()
    const { key, value, type = 'string', description, isPublic = false } = body

    if (!key || value === undefined) {
      return NextResponse.json(
        { error: 'Key and value are required' },
        { status: 400 }
      )
    }

    // Get user from database
    const user = await userQueries.findByEmail(session.user.email)
    if (!user) {
      return NextResponse.json({ error: 'User not found' }, { status: 404 })
    }

    // Create or update variable
    const variable = await dbHelpers.updateUserVariable(
      user.id,
      key,
      value,
      type,
      description
    )

    return NextResponse.json({
      success: true,
      variable: {
        id: variable.id,
        key: variable.key,
        value: variable.value,
        jsonValue: variable.jsonValue,
        type: variable.type,
        description: variable.description,
        isPublic: variable.isPublic,
        createdAt: variable.createdAt?.toISOString(),
        updatedAt: variable.updatedAt?.toISOString()
      }
    })
  } catch (error) {
    console.error('Error creating user variable:', error)
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    )
  }
}

export async function PUT(request: NextRequest) {
  try {
    const session = await getServerSession(authOptions)
    
    if (!session?.user?.email) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
    }

    const body = await request.json()
    const { variables } = body

    if (!variables || !Array.isArray(variables)) {
      return NextResponse.json(
        { error: 'Variables array is required' },
        { status: 400 }
      )
    }

    // Get user from database
    const user = await userQueries.findByEmail(session.user.email)
    if (!user) {
      return NextResponse.json({ error: 'User not found' }, { status: 404 })
    }

    // Bulk update variables
    const results = await dbHelpers.bulkUpdateVariables(
      user.id,
      variables.reduce((acc, variable) => {
        acc[variable.key] = {
          value: variable.value,
          type: variable.type,
          description: variable.description
        }
        return acc
      }, {})
    )

    return NextResponse.json({
      success: true,
      updated: results.length,
      variables: results
    })
  } catch (error) {
    console.error('Error bulk updating variables:', error)
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    )
  }
}

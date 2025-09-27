import { NextRequest, NextResponse } from 'next/server'
import { getServerSession } from 'next-auth'
import { authOptions } from '@/lib/auth'
import { userQueries, userVariableQueries } from '@/lib/db/queries'
import { dbHelpers } from '@/lib/db/utils'

export async function GET(
  request: NextRequest,
  { params }: { params: { key: string } }
) {
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

    // Get specific variable
    const variable = await dbHelpers.getUserVariable(user.id, params.key)
    
    if (!variable) {
      return NextResponse.json({ error: 'Variable not found' }, { status: 404 })
    }

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
    console.error('Error getting user variable:', error)
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    )
  }
}

export async function PUT(
  request: NextRequest,
  { params }: { params: { key: string } }
) {
  try {
    const session = await getServerSession(authOptions)
    
    if (!session?.user?.email) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
    }

    const body = await request.json()
    const { value, type, description, isPublic } = body

    if (value === undefined) {
      return NextResponse.json(
        { error: 'Value is required' },
        { status: 400 }
      )
    }

    // Get user from database
    const user = await userQueries.findByEmail(session.user.email)
    if (!user) {
      return NextResponse.json({ error: 'User not found' }, { status: 404 })
    }

    // Update variable
    const variable = await dbHelpers.updateUserVariable(
      user.id,
      params.key,
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
    console.error('Error updating user variable:', error)
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    )
  }
}

export async function DELETE(
  request: NextRequest,
  { params }: { params: { key: string } }
) {
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

    // Check if variable exists
    const existingVariable = await userVariableQueries.getByKey(user.id, params.key)
    if (!existingVariable) {
      return NextResponse.json({ error: 'Variable not found' }, { status: 404 })
    }

    // Delete variable
    await userVariableQueries.delete(existingVariable.id)

    return NextResponse.json({
      success: true,
      message: 'Variable deleted successfully'
    })
  } catch (error) {
    console.error('Error deleting user variable:', error)
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    )
  }
}

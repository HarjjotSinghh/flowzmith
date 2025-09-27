import sql from "@/app/api/utils/sql";

// Get single contract
export async function GET(request, { params }) {
  try {
    const { id } = params;
    
    const result = await sql`
      SELECT * FROM contracts WHERE id = ${id}
    `;
    
    if (result.length === 0) {
      return Response.json({ error: 'Contract not found' }, { status: 404 });
    }
    
    return Response.json(result[0]);
  } catch (error) {
    console.error('Error fetching contract:', error);
    return Response.json({ error: 'Failed to fetch contract' }, { status: 500 });
  }
}

// Update contract
export async function PUT(request, { params }) {
  try {
    const { id } = params;
    const updates = await request.json();
    
    // Build dynamic update query
    const setClause = [];
    const values = [];
    let paramIndex = 1;
    
    for (const [key, value] of Object.entries(updates)) {
      if (['name', 'description', 'contract_code', 'compiled_bytecode', 'deployed_address', 'network', 'status'].includes(key)) {
        setClause.push(`${key} = $${paramIndex}`);
        values.push(value);
        paramIndex++;
      }
    }
    
    if (setClause.length === 0) {
      return Response.json({ error: 'No valid fields to update' }, { status: 400 });
    }
    
    setClause.push(`updated_at = CURRENT_TIMESTAMP`);
    values.push(id);
    
    const query = `UPDATE contracts SET ${setClause.join(', ')} WHERE id = $${paramIndex} RETURNING *`;
    const result = await sql(query, values);
    
    if (result.length === 0) {
      return Response.json({ error: 'Contract not found' }, { status: 404 });
    }
    
    return Response.json(result[0]);
  } catch (error) {
    console.error('Error updating contract:', error);
    return Response.json({ error: 'Failed to update contract' }, { status: 500 });
  }
}

// Delete contract
export async function DELETE(request, { params }) {
  try {
    const { id } = params;
    
    const result = await sql`
      DELETE FROM contracts WHERE id = ${id} RETURNING *
    `;
    
    if (result.length === 0) {
      return Response.json({ error: 'Contract not found' }, { status: 404 });
    }
    
    return Response.json({ message: 'Contract deleted successfully' });
  } catch (error) {
    console.error('Error deleting contract:', error);
    return Response.json({ error: 'Failed to delete contract' }, { status: 500 });
  }
}
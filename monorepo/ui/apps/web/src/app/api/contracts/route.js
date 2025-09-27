import sql from "@/app/api/utils/sql";

// Get all contracts
export async function GET(request) {
  try {
    const { searchParams } = new URL(request.url);
    const status = searchParams.get('status');
    
    let query = 'SELECT * FROM contracts';
    let params = [];
    
    if (status) {
      query += ' WHERE status = $1';
      params.push(status);
    }
    
    query += ' ORDER BY updated_at DESC';
    
    const contracts = await sql(query, params);
    return Response.json(contracts);
  } catch (error) {
    console.error('Error fetching contracts:', error);
    return Response.json({ error: 'Failed to fetch contracts' }, { status: 500 });
  }
}

// Create new contract
export async function POST(request) {
  try {
    const { name, description } = await request.json();
    
    if (!name) {
      return Response.json({ error: 'Contract name is required' }, { status: 400 });
    }
    
    const result = await sql`
      INSERT INTO contracts (name, description, status)
      VALUES (${name}, ${description || ''}, 'draft')
      RETURNING *
    `;
    
    return Response.json(result[0]);
  } catch (error) {
    console.error('Error creating contract:', error);
    return Response.json({ error: 'Failed to create contract' }, { status: 500 });
  }
}
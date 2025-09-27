import sql from "@/app/api/utils/sql";

// Get all components
export async function GET(request) {
  try {
    const { searchParams } = new URL(request.url);
    const category = searchParams.get('category');
    
    let query = 'SELECT * FROM components';
    let params = [];
    
    if (category) {
      query += ' WHERE category = $1';
      params.push(category);
    }
    
    query += ' ORDER BY category, name';
    
    const components = await sql(query, params);
    return Response.json(components);
  } catch (error) {
    console.error('Error fetching components:', error);
    return Response.json({ error: 'Failed to fetch components' }, { status: 500 });
  }
}
export async function onRequest({ request, env }) {
  const headers = {
    'Access-Control-Allow-Origin': '*',
    'Cache-Control': 'no-store',
  };

  const pageRes = await fetch(`https://api.notion.com/v1/pages/${env.COUNT_PAGE_ID}`, {
    headers: {
      'Authorization': `Bearer ${env.NOTION_TOKEN}`,
      'Notion-Version': '2022-06-28',
      'Cache-Control': 'no-cache',
    }
  });
  const page = await pageRes.json();
  const current = page.properties?.['上限金額']?.number || 0;

  if (request.method === 'POST') {
    const newCount = current + 1;
    await fetch(`https://api.notion.com/v1/pages/${env.COUNT_PAGE_ID}`, {
      method: 'PATCH',
      headers: {
        'Authorization': `Bearer ${env.NOTION_TOKEN}`,
        'Notion-Version': '2022-06-28',
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        properties: { '上限金額': { number: newCount } }
      })
    });
    return Response.json({ count: newCount }, { headers });
  }
  return Response.json({ count: current }, { headers });
}

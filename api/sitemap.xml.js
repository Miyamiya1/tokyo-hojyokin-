// public/sitemap.xml と同じ内容(tools/build.py が両方を生成)
export default function handler(req, res) {
  res.setHeader('Content-Type', 'application/xml; charset=utf-8');
  res.status(200).send(`<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url><loc>https://tokyo-hojyokin.vercel.app/</loc><lastmod>2026-11-02</lastmod></url>
  <url><loc>https://tokyo-hojyokin.vercel.app/hojyo/</loc><lastmod>2026-11-02</lastmod></url>
  <url><loc>https://tokyo-hojyokin.vercel.app/hojyo/tokyo-chikudenchi-r8.html</loc><lastmod>2026-11-02</lastmod></url>
  <url><loc>https://tokyo-hojyokin.vercel.app/hojyo/tokyo-mado-door-r8.html</loc><lastmod>2026-11-02</lastmod></url>
  <url><loc>https://tokyo-hojyokin.vercel.app/hojyo/tokyo-dannetsu-yokuso-r8.html</loc><lastmod>2026-11-02</lastmod></url>
</urlset>
`);
}

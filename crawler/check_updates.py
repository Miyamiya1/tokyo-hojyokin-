import urllib.request, json, os, hashlib

NOTION_TOKEN = os.environ["NOTION_TOKEN"]
DB_ID = os.environ["NOTION_DB_ID"]
CLAUDE_KEY = os.environ["CLAUDE_API_KEY"]

headers_notion = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}

def get_all_pages():
    all_pages = []
    cursor = None
    while True:
        body = {"page_size": 100}
        if cursor:
            body["start_cursor"] = cursor
        req = urllib.request.Request(
            f"https://api.notion.com/v1/databases/{DB_ID}/query",
            data=json.dumps(body).encode(),
            headers=headers_notion, method="POST"
        )
        with urllib.request.urlopen(req) as res:
            data = json.loads(res.read())
        all_pages.extend(data["results"])
        if not data["has_more"]:
            break
        cursor = data["next_cursor"]
    return all_pages

def check_url(url):
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        req.get_method = lambda: "HEAD"
        with urllib.request.urlopen(req, timeout=10) as res:
            return res.status, None
    except Exception as e:
        return None, str(e)

pages = get_all_pages()
print(f"総件数: {len(pages)}件")

errors = []
for page in pages:
    title = page["properties"]["名前"]["title"]
    url = page["properties"]["公式URL"]["url"]
    if not title or not url:
        continue
    name = title[0]["text"]["content"]
    status, err = check_url(url)
    if status is None or status >= 400:
        errors.append({"name": name, "url": url, "error": err or f"HTTP {status}"})
        print(f"❌ {name[:40]} → {err or status}")
    else:
        print(f"✓ {name[:40]}")

print(f"\n問題あり: {len(errors)}件")
if errors:
    print("\n=== 要修正リスト ===")
    for e in errors:
        print(f"- {e['name']}: {e['url']}")

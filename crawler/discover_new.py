import urllib.request, urllib.parse, json, os, re
from html.parser import HTMLParser

NOTION_TOKEN = os.environ["NOTION_TOKEN"]
DB_ID = os.environ["NOTION_DB_ID"]
CLAUDE_KEY = os.environ["CLAUDE_API_KEY"]

headers_notion = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}

TARGETS = [
    {"area": "横浜市", "url": "https://www.city.yokohama.lg.jp/kurashi/sumai-kurashi/jutaku/sien/"},
    {"area": "横浜市", "url": "https://www.city.yokohama.lg.jp/business/kigyoshien/keieishien/"},
    {"area": "川崎市", "url": "https://www.city.kawasaki.jp/280/category/30-0-0-0-0-0-0-0-0-0.html"},
    {"area": "鎌倉市", "url": "https://www.city.kamakura.kanagawa.jp/kosodate/"},
    {"area": "藤沢市", "url": "https://www.city.fujisawa.kanagawa.jp/kodomo-se/teate_kyufu.html"},
    {"area": "横須賀市", "url": "https://www.city.yokosuka.kanagawa.jp/sangyo/keizai/shinko/index.html"},
    {"area": "平塚市", "url": "https://www.city.hiratsuka.kanagawa.jp/sangyo/page33_00038.html"},
    {"area": "相模原市", "url": "https://www.city.sagamihara.kanagawa.jp/kurashi/1026489/sumai/1026513/index.html"},
    {"area": "厚木市", "url": "https://www.city.atsugi.kanagawa.jp/kosodate_kyoiku/teate_josei/index.html"},
    {"area": "茅ヶ崎市", "url": "https://www.city.chigasaki.kanagawa.jp/sangyo/1043316/index.html"},
    {"area": "茅ヶ崎市", "url": "https://www.city.chigasaki.kanagawa.jp/kosodate/1024750/index.html"},
    {"area": "大和市", "url": "https://www.city.yamato.lg.jp/gyosei/soshik/40/sangyo/shogyo/shien_seibi_todokede/4243.html"},
    {"area": "大和市", "url": "https://www.city.yamato.lg.jp/section/ehon_no_machi/age/B/B00010.html"},
    {"area": "三浦市", "url": "https://www.city.miura.kanagawa.jp/shigoto_sangyo_machizukuri/sangyoshinko/6/shoukou2/index.html"},
    {"area": "逗子市", "url": "https://www.city.zushi.kanagawa.jp/kurashi/gomirecycle/1002120/index.html"},
    {"area": "秦野市", "url": "https://www.city.hadano.kanagawa.jp/www/genre/0000000000000/1000000000261/index.html"},
    {"area": "伊勢原市", "url": "https://www.city.isehara.kanagawa.jp/docs/2013111500015/"},
    {"area": "海老名市", "url": "https://www.city.ebina.kanagawa.jp/kurashi/shien/josei/index.html"},
    {"area": "座間市", "url": "https://www.city.zama.kanagawa.jp/www/genre/0000000000000/1000000000150/index.html"},
    {"area": "綾瀬市", "url": "https://www.city.ayase.kanagawa.jp/kurashi/shien/josei/index.html"},
    {"area": "南足柄市", "url": "https://www.city.minamiashigara.kanagawa.jp/kurashi/shien/"},
    {"area": "小田原市", "url": "https://www.city.odawara.kanagawa.jp/field/edu-ch/kosodate/assistance/"},
    {"area": "小田原市", "url": "https://www.city.odawara.kanagawa.jp/field/industry/industrial_promotion/p29957.html"},
    {"area": "箱根町", "url": "https://www.town.hakone.kanagawa.jp/www/contents/1100000002059/index.html"},
    {"area": "湯河原町", "url": "https://www.town.yugawara.kanagawa.jp/soshiki/17/28755.html"},
    {"area": "松田町", "url": "https://town.matsuda.kanagawa.jp/site/teiju-syoushi/"},
    {"area": "山北町", "url": "https://www.town.yamakita.kanagawa.jp/0000006711.html"},
    {"area": "中井町", "url": "https://www.town.nakai.kanagawa.jp/soshiki/kikakukaseisakuhan/sumai/1/1/404.html"},
    {"area": "大井町", "url": "https://www.town.oi.kanagawa.jp/site/iju/"},
    {"area": "大磯町", "url": "https://www.town.oiso.kanagawa.jp/kurashi/jutaku/"},
    {"area": "二宮町", "url": "https://www.town.ninomiya.kanagawa.jp/0000000113.html"},
    {"area": "寒川町", "url": "https://www.town.samukawa.kanagawa.jp/kurashi/shien/"},
    {"area": "清川村", "url": "https://www.town.kiyokawa.kanagawa.jp/soshiki/sangyokanko/akiyasumai/1114.html"},
    {"area": "愛川町", "url": "https://www.town.aikawa.kanagawa.jp/kurashi/shien/"},
    {"area": "葉山町", "url": "https://www.town.hayama.lg.jp/soshiki/seisaku/3202.html"},
    {"area": "寒川町", "url": "https://www.town.samukawa.kanagawa.jp/kurashi/shien/josei/"},
    {"area": "神奈川県", "url": "https://www.pref.kanagawa.jp/docs/f2g/cnt/f4085/index.html"},
    {"area": "神奈川県", "url": "https://www.pref.kanagawa.jp/docs/v3e/jyosei/gakuhisien/"},
]

def get_existing_urls():
    urls = set()
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
        for p in data["results"]:
            url = p["properties"]["公式URL"]["url"]
            if url:
                urls.add(url)
        if not data["has_more"]:
            break
        cursor = data["next_cursor"]
    return urls

def fetch_page(url):
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=10) as res:
            html = res.read().decode("utf-8", errors="ignore")
        # タイトルと本文テキストを抽出
        title_match = re.search(r'<title[^>]*>([^<]+)</title>', html, re.IGNORECASE)
        title = title_match.group(1).strip() if title_match else ""
        # HTMLタグを除去してテキスト取得（最初の500文字）
        text = re.sub(r'<[^>]+>', ' ', html)
        text = re.sub(r'\s+', ' ', text).strip()[:500]
        return title, text, html
    except:
        return "", "", ""

def extract_links(html, base_url):
    links = []
    parsed_base = urllib.parse.urlparse(base_url)
    pattern = r'href=["\']([^"\'#?]+)["\']'
    for match in re.finditer(pattern, html):
        href = match.group(1)
        if href.startswith("http"):
            link = href
        elif href.startswith("/"):
            link = f"{parsed_base.scheme}://{parsed_base.netloc}{href}"
        else:
            continue
        if parsed_base.netloc in link and link not in links:
            links.append(link)
    return links

def ask_claude(url, title, text, area):
    prompt = f"""以下のページが{area}の補助金・助成金・支援金・給付金・奨学金のページかどうか判断してください。

URL: {url}
タイトル: {title}
本文（抜粋）: {text[:300]}

判断基準：
- 個人または事業者が申請できる補助金・助成金・支援金・給付金・奨学金 → YES
- 募集終了・廃止済みの制度 → NO
- トップページ・お知らせ・採用・議会・統計 → NO
- 補助金と無関係なページ → NO

JSON形式のみで回答：
{{"is_subsidy": true/false, "title": "制度の正式名称", "category": "事業者向け/子育て・教育/住まい・住宅/介護・福祉のいずれか", "target": "個人/事業者"}}"""

    data = json.dumps({
        "model": "claude-haiku-4-5-20251001",
        "max_tokens": 200,
        "messages": [{"role": "user", "content": prompt}]
    }).encode()

    req = urllib.request.Request(
        "https://api.anthropic.com/v1/messages",
        data=data,
        headers={
            "x-api-key": CLAUDE_KEY,
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json"
        }
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as res:
            result = json.loads(res.read())
            text = result["content"][0]["text"].strip()
            match = re.search(r'\{.*\}', text, re.DOTALL)
            if match:
                return json.loads(match.group())
    except:
        pass
    return None

def add_to_notion(title, area, category, target, url):
    props = {
        "名前": {"title": [{"text": {"content": title}}]},
        "対象": {"select": {"name": target}},
        "カテゴリ": {"select": {"name": category}},
        "市区町村": {"rich_text": [{"text": {"content": area}}]},
        "公式URL": {"url": url}
    }
    data = json.dumps({"parent": {"database_id": DB_ID}, "properties": props}).encode()
    req = urllib.request.Request(
        "https://api.notion.com/v1/pages",
        data=data,
        headers=headers_notion,
        method="POST"
    )
    urllib.request.urlopen(req)

# まず間違って追加されたデータを削除
print("不正確なデータを削除中...")
req = urllib.request.Request(
    f"https://api.notion.com/v1/databases/{DB_ID}/query",
    data=json.dumps({"page_size": 100}).encode(),
    headers=headers_notion, method="POST"
)
with urllib.request.urlopen(req) as res:
    pages = json.loads(res.read())["results"]

# 今回追加された疑わしいデータを削除（タイトルが短すぎるか汎用的なもの）
deleted = 0
for page in pages:
    t = page["properties"]["名前"]["title"]
    if not t:
        continue
    title = t[0]["text"]["content"]
    if title in ["産業振興補助金・助成金", "子育て支援", "補助金・助成金・支援金"]:
        req2 = urllib.request.Request(
            f"https://api.notion.com/v1/pages/{page['id']}",
            data=json.dumps({"archived": True}).encode(),
            headers=headers_notion, method="PATCH"
        )
        urllib.request.urlopen(req2)
        deleted += 1
        print(f"削除: {title}")

print(f"削除完了: {deleted}件")

# 新規発見
existing_urls = get_existing_urls()
print(f"\n既存URL数: {len(existing_urls)}")

added = 0
for target in TARGETS:
    print(f"\n{target['area']}を巡回中...")
    title_page, text_page, html = fetch_page(target["url"])
    if not html:
        print("取得失敗")
        continue

    links = extract_links(html, target["url"])
    new_links = [l for l in links if l not in existing_urls]
    new_links = list(set(new_links))[:5]
    print(f"新規候補: {len(new_links)}件")

    for link in new_links:
        link_title, link_text, _ = fetch_page(link)
        if not link_title:
            continue
        result = ask_claude(link, link_title, link_text, target["area"])
        if result and result.get("is_subsidy"):
            try:
                add_to_notion(result["title"], target["area"], result["category"], result["target"], link)
                print(f"✓ 追加: {result['title'][:40]}")
                added += 1
            except Exception as e:
                print(f"✗ 失敗: {e}")

print(f"\n新規追加: {added}件")

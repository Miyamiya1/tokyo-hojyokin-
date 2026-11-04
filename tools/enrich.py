"""各補助金の公式ページから、概要・金額・対象・締切の手がかりを抜き出す(短い抜粋のみ。出典リンクを必ず併記する前提)
入力: data/subsidies_snapshot.json  出力: data/enriched.json"""
import json, re, time, os, urllib.request, html
from concurrent.futures import ThreadPoolExecutor
D = os.path.join(os.path.dirname(__file__), "..", "data")
S = json.load(open(os.path.join(D, "subsidies_snapshot.json")))
OUT = os.path.join(D, "enriched.json")
done = {x["id"]: x for x in json.load(open(OUT))} if os.path.exists(OUT) else {}
UA = {"User-Agent": "Mozilla/5.0 (compatible; hojyokin-search/1.0; +https://tokyo-hojyokin.pages.dev)"}

def text_of(raw):
    raw = re.sub(r"(?is)<(script|style|noscript|header|footer|nav)[^>]*>.*?</\1>", " ", raw)
    meta = re.search(r'(?is)<meta[^>]+name=["\']description["\'][^>]+content=["\']([^"\']+)', raw)
    body = re.sub(r"(?s)<[^>]+>", "\n", raw)
    lines = [html.unescape(l).strip() for l in body.split("\n")]
    lines = [re.sub(r"\s+", " ", l) for l in lines if len(l.strip()) >= 12]
    return (html.unescape(meta.group(1)).strip() if meta else ""), lines

def grab(x):
    try:
        req = urllib.request.Request(x["url"], headers=UA)
        raw = urllib.request.urlopen(req, timeout=20).read()
        enc = "utf-8"
        m = re.search(rb'charset=["\']?([A-Za-z0-9_-]+)', raw[:3000])
        if m: enc = m.group(1).decode()
        t = raw.decode(enc, errors="ignore")
    except Exception as e:
        return dict(x, ok=False, err=str(e)[:80])
    meta, lines = text_of(t)
    title_words = set(re.findall(r"[一-龥ァ-ヶー]{2,}", x["title"]))
    # 概要: 補助金名の語を含む、または「対象」「支給」「助成」を含む行を優先して最大3行・計200字
    cand = [l for l in lines if any(w in l for w in ("助成", "補助", "支給", "給付", "対象", "支援", "手当")) and 15 <= len(l) <= 160]
    summary = ""
    for l in cand:
        if l in summary: continue
        if len(summary) + len(l) > 200: break
        summary += l + " "
    amounts = sorted({m for l in lines for m in re.findall(r"(?:上限|最大|月額|年額|1人あたり|一人あたり)?\s*[0-9０-９,，.]+\s*(?:万円|円)", l)}, key=len)[:4]
    dl = [l for l in lines if re.search(r"(申請期限|申請期間|受付期間|締切|〆切|募集期間)", l) and len(l) <= 120][:2]
    tg = [l for l in lines if re.search(r"(対象者|対象となる方|支給対象|助成対象|補助対象)", l) and len(l) <= 140][:2]
    return dict(x, ok=True, meta=meta[:200], summary=summary.strip()[:220], amounts=amounts, deadline=dl, target_lines=tg)

todo = [x for x in S if x["id"] not in done]
print("取得対象", len(todo), "件", flush=True)
def slow(x):
    r = grab(x); time.sleep(1.2); return r
with ThreadPoolExecutor(3) as ex:
    for i, r in enumerate(ex.map(slow, todo), 1):
        done[r["id"]] = r
        if i % 25 == 0:
            json.dump(list(done.values()), open(OUT, "w"), ensure_ascii=False); print(i, flush=True)
json.dump(list(done.values()), open(OUT, "w"), ensure_ascii=False)
ok = [v for v in done.values() if v.get("ok")]
print("完了", len(done), "取得成功", len(ok), "概要あり", sum(1 for v in ok if v["summary"] or v["meta"]), "金額あり", sum(1 for v in ok if v["amounts"]))

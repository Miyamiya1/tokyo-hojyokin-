"""
補助金の個別ページ(静的HTML)を生成する。検索エンジンに中身が読まれるよう、内容はHTMLに直接書き込む
- 内容は公式ページを人(Claude)が確認して書いたもの(PROGRAMS)。自動抽出は使わない
- 出力: public/hojyo/*.html, public/hojyo/index.html, public/sitemap.xml, public/robots.txt
使い方: python tools/build.py
"""
import html, json, os
from datetime import date

ROOT = os.path.join(os.path.dirname(__file__), "..")
PUB = os.path.join(ROOT, "public")
SITE = "https://tokyo-hojyokin.pages.dev"
CHECKED = "2026-11-02"
os.makedirs(os.path.join(PUB, "hojyo"), exist_ok=True)

PROGRAMS = [
    dict(
        slug="tokyo-chikudenchi-r8",
        title="東京都の蓄電池補助金(令和8年度)",
        catch="家庭用蓄電池に1kWhあたり10万円、上限120万円",
        description="東京都(クール・ネット東京)の令和8年度「家庭における蓄電池導入促進事業」。蓄電容量1kWhあたり10万円、DR実証に参加しない場合の上限は1戸120万円。対象・計算方法・申請の流れを公式情報をもとにまとめました。",
        official_name="令和8年度 家庭における蓄電池導入促進事業",
        official_url="https://www.tokyo-co2down.jp/subsidy/family_tikudenchi/r8/",
        org="東京都・公益財団法人東京都環境公社(クール・ネット東京)",
        summary=[("対象者", "都内の住宅に設置した蓄電池の所有者(国・地方公共団体を除く)"),
                 ("助成額", "蓄電容量1kWhあたり10万円(税抜の対象経費が上限)。DR実証に参加しない場合は1戸あたり上限120万円"),
                 ("受付", "事前申込:令和8年5月29日開始 / 交付申請兼実績報告:令和8年6月30日開始"),
                 ("申請窓口", "クール・ネット東京(オンライン申請)")],
        sections=[
            ("対象となる蓄電池", ["都内の住宅に新規に設置された機器であること",
                              "設置期間は令和8年4月1日から令和11年3月30日まで(公式ページの表記)",
                              "国の補助事業の対象機器として、環境共創イニシアチブ(SII)に登録された機器であること",
                              "令和8年10月1日以降に事前申込する場合は、令和8年度の登録済製品一覧に載った機器に限られる(4〜6月に契約等をした場合を除く)",
                              "都・東京都環境公社の同種の助成金と重複して受けていないこと"]),
            ("助成額の計算", ["蓄電池システム(パッケージ):蓄電容量×10万円。DR実証に参加しない場合は1戸あたり上限120万円",
                          "DR実証に参加する場合:蓄電容量×10万円+DR実証参加10万円+(エネルギーマネジメント機器・IoT関連機器の設置台数×5万円)",
                          "蓄電池ユニットの増設:蓄電容量×6万円。DR実証に参加しない場合は1戸あたり上限72万円",
                          "いずれも、税抜の助成対象経費(国・他の自治体の補助金を差し引いた額)との小さい方が助成額",
                          "リフォーム瑕疵保険等:1契約あたり7,000円"]),
            ("申請の流れ", ["認証用メールアドレスを登録する",
                         "事前申込フォームから申し込む",
                         "設置・支払いの後、交付申請兼実績報告フォームから申請する(事前申込の受理から1年以内)",
                         "DR実証に参加する場合、DR実証契約は交付申請兼実績報告より前に結ぶ"]),
            ("注意点", ["令和8年度の事前申込分は、実績報告のときに金融機関発行の証明書等の提出が必須",
                      "キャッシュバックや商品券・ポイントなどの現金同等物は、助成対象経費から差し引かれる",
                      "交付申請兼実績報告の受付後にDR実証契約を結んでも、DR加算は適用されない",
                      "お住まいの区市町村にも上乗せの助成がある場合があるため、あわせて確認する"]),
        ],
        contact="創エネ支援チーム 蓄電池ヘルプデスク 03-6737-5100(平日9:00〜17:00、祝祭日・年末年始を除く)",
        affiliate_kind="battery",
    ),
    dict(
        slug="tokyo-mado-door-r8",
        title="東京都の窓・ドアの断熱リフォーム補助金(令和8年度)",
        catch="高断熱窓・ドアに1住戸あたり上限200万円(断熱防犯窓は300万円)",
        description="東京都(クール・ネット東京)の令和8年度「既存住宅における省エネ改修促進事業」のうち高断熱窓・ドア。製品の性能と大きさに応じた単価の合計を助成、上限は1住戸200万円(断熱防犯窓は300万円)。単価表と申請の流れをまとめました。",
        official_name="令和8年度 既存住宅における省エネ改修促進事業(高断熱窓・ドア・断熱材・浴槽)",
        official_url="https://www.tokyo-co2down.jp/subsidy/ene_reform/ene_reform_r08/",
        org="東京都・公益財団法人東京都環境公社(クール・ネット東京)",
        summary=[("対象者", "都内に住宅を所有する個人・法人・管理組合(共同申請のリース事業者を含む)"),
                 ("助成額", "製品の性能(グレード)と大きさに応じた単価の合計。上限は1住戸あたり200万円、断熱防犯窓は300万円"),
                 ("最低申請額", "窓とドアの助成額の合計が5万円以上の工事"),
                 ("受付", "事前申込:令和8年5月29日から / 交付申請兼実績報告:令和8年6月30日〜令和11年3月30日")],
        sections=[
            ("対象となる工事", ["都内の既存住宅に、令和8年4月1日以降に新たに設置するもの(新築は対象外、未使用品に限る)",
                             "高断熱窓:国の補助事業等で対象製品として登録された窓・ガラス",
                             "高断熱ドア:屋外から施錠できる建具で、熱貫流率2.3 W/(㎡・K)以下のもの"]),
            ("内窓設置の助成単価(1か所あたり)", ["グレードP(熱貫流率1.1以下):特大13.3万円/大10.6万円/中7.2万円/小4.6万円",
                                         "グレードS(1.1超〜1.5以下):特大8.2万円/大6.5万円/中4.4万円/小2.8万円",
                                         "グレードA(1.5超〜1.9以下):特大3.2万円/大2.6万円/中1.8万円/小1.2万円",
                                         "グレードB(1.9超〜2.3以下):特大2.0万円/大1.6万円/中1.3万円/小1.0万円",
                                         "大きさの区分:特大4.0㎡以上/大2.8〜4.0㎡未満/中1.6〜2.8㎡未満/小0.2〜1.6㎡未満"]),
            ("外窓交換・ドア交換の助成単価", ["外窓交換(はつり・カバー工法)グレードP:特大27.7万円/大22.0万円/中16.3万円/小10.9万円",
                                       "外窓交換グレードS:特大18.7万円/大14.9万円/中11.0万円/小7.4万円",
                                       "ドア交換:グレードP 22.0万円/S 14.9万円/A 11.7万円/B 7.8万円",
                                       "ガラス交換・断熱防犯窓・外窓A/Bグレードの単価は公式ページの単価表を参照"]),
            ("申請の流れ", ["事前申込(必須)。工事の契約・施工は事前申込の受付後が条件",
                         "工事業者と契約し、工事・支払いを行う",
                         "事前申込から1年以内に交付申請兼実績報告を行う",
                         "審査・交付決定の後、口座に助成金が振り込まれる"]),
            ("注意点", ["工事の前にアスベスト含有建材の事前調査が必要",
                      "キャッシュバック等の現金同等物は助成対象経費から差し引かれる",
                      "都・東京都環境公社の同種の助成金とは重複して受けられない",
                      "予算(事業全体で約1,012億円)がなくなり次第、受付が終わる可能性がある"]),
        ],
        contact="創エネ支援チーム 03-6737-5300(平日9:00〜17:00、12:00〜13:00を除く。2026年9月1日に番号変更)",
        affiliate_kind="reform",
    ),
    dict(
        slug="tokyo-dannetsu-yokuso-r8",
        title="東京都の断熱材・高断熱浴槽の補助金(令和8年度)",
        catch="断熱材は対象経費の1/3・上限100万円、高断熱浴槽は9.5万円",
        description="東京都(クール・ネット東京)の令和8年度「既存住宅における省エネ改修促進事業」のうち断熱材と高断熱浴槽。断熱材は対象経費の1/3(上限1住戸100万円)、高断熱浴槽は1住戸9.5万円。条件と申請の流れをまとめました。",
        official_name="令和8年度 既存住宅における省エネ改修促進事業(高断熱窓・ドア・断熱材・浴槽)",
        official_url="https://www.tokyo-co2down.jp/subsidy/ene_reform/ene_reform_r08/",
        org="東京都・公益財団法人東京都環境公社(クール・ネット東京)",
        summary=[("対象者", "都内に住宅を所有する個人・法人・管理組合(共同申請のリース事業者を含む)"),
                 ("断熱材", "対象経費の1/3、1住戸あたり上限100万円(国の補助金を受ける場合はその交付額が上限)"),
                 ("高断熱浴槽", "1住戸あたり9.5万円"),
                 ("受付", "事前申込:令和8年5月29日から / 交付申請兼実績報告:令和8年6月30日〜令和11年3月30日")],
        sections=[
            ("断熱材の条件", ["居室の外気に接する部分すべてに断熱材を設置し部位ごとの基準を満たす、または改修後の住宅が断熱性能等級5以上",
                           "熱抵抗値の基準:天井2.7以上、外壁2.7以上、床2.2以上",
                           "都内の既存住宅に令和8年4月1日以降に設置するもの(新築は対象外)"]),
            ("高断熱浴槽の条件", ["JIS A5532:2011に規定する高断熱浴槽と同等以上の性能を持つもの"]),
            ("申請の流れ", ["事前申込(必須)。工事の契約・施工は事前申込の受付後が条件",
                         "工事業者と契約し、工事・支払いを行う",
                         "事前申込から1年以内に交付申請兼実績報告を行う",
                         "審査・交付決定の後、口座に助成金が振り込まれる"]),
            ("注意点", ["窓・ドアの改修と同じ事業なので、同時に申請する場合は窓・ドアの条件もあわせて確認する",
                      "工事の前にアスベスト含有建材の事前調査が必要",
                      "キャッシュバック等の現金同等物は助成対象経費から差し引かれる"]),
        ],
        contact="創エネ支援チーム 03-6737-5300(平日9:00〜17:00、12:00〜13:00を除く。2026年9月1日に番号変更)",
        affiliate_kind="reform",
    ),
]

CSS = """*{margin:0;padding:0;box-sizing:border-box}body{font-family:-apple-system,BlinkMacSystemFont,'Helvetica Neue','Hiragino Sans',sans-serif;background:#f5f5f5;color:#333;line-height:1.8}
header{background:#1a5276;color:#fff;padding:16px 20px}header a{color:#fff;text-decoration:none;font-weight:600}
main{max-width:820px;margin:0 auto;padding:20px}nav.crumb{font-size:12px;color:#666;margin-bottom:12px}nav.crumb a{color:#1a5276}
h1{font-size:22px;line-height:1.5;margin-bottom:6px}.catch{font-size:16px;color:#1a5276;font-weight:600;margin-bottom:16px}
.box{background:#fff;border:1px solid #e5e5e5;border-radius:12px;padding:16px 20px;margin-bottom:16px}
table{width:100%;border-collapse:collapse}th,td{text-align:left;vertical-align:top;padding:8px 6px;border-bottom:1px solid #eee;font-size:14px}th{width:28%;color:#1a5276;white-space:nowrap}
h2{font-size:17px;margin:4px 0 8px;color:#1a5276}ul{padding-left:1.2em}li{font-size:14px;margin:2px 0}
.src{font-size:13px;color:#555}.src a{color:#1a5276}.note{font-size:12px;color:#777}
.pr{display:inline-block;font-size:11px;color:#777;border:1px solid #bbb;border-radius:4px;padding:0 6px;margin-bottom:4px}.ad ul{padding-left:0}.ad li{list-style:none;margin:6px 0}.ad a{color:#1a5276;font-weight:600}
.btn{display:inline-block;background:#1a5276;color:#fff;text-decoration:none;padding:8px 14px;border-radius:8px;font-size:14px}
.list a{display:block;padding:10px 0;border-bottom:1px solid #eee;color:#1a5276;text-decoration:none}.list span{display:block;font-size:13px;color:#555}
footer{max-width:820px;margin:0 auto;padding:20px;font-size:12px;color:#777}"""

# A8.netの広告(テキスト広告・通常広告用)。コードはNotion「A8広告コード」と同じ。1x1の計測画像は消さない
AFFILIATE = {
    "battery": [
        '<a href="https://px.a8.net/svt/ejp?a8mat=4BGBN3+FH9R02+2AG2+15S78I" rel="nofollow">蓄電池の無料一括比較サイト【タイナビ蓄電池】</a>'
        '<img border="0" width="1" height="1" src="https://www13.a8.net/0.gif?a8mat=4BGBN3+FH9R02+2AG2+15S78I" alt="">',
        '<a href="https://px.a8.net/svt/ejp?a8mat=4BGBN3+FGOBEA+5CRG+5YJRM" rel="nofollow">【エコ×エネの相談窓口】完全無料の蓄電池一括見積もり</a>'
        '<img border="0" width="1" height="1" src="https://www12.a8.net/0.gif?a8mat=4BGBN3+FGOBEA+5CRG+5YJRM" alt="">',
    ],
    "reform": [
        '<a href="https://px.a8.net/svt/ejp?a8mat=4BGBN3+FJNHF6+46CI+60OXE" rel="nofollow">リフォーム比較プロで見積もり比較</a>'
        '<img border="0" width="1" height="1" src="https://www16.a8.net/0.gif?a8mat=4BGBN3+FJNHF6+46CI+60OXE" alt="">',
    ],
}
AD_LEAD = {
    "battery": "助成額は税抜の対象経費が上限なので、設置費用そのものを抑えることも大切です。複数の業者の見積もりを無料で比べられるサービスがあります。",
    "reform": "助成額は製品と工事内容で決まるため、工事費は業者によって差が出やすいところです。複数の業者の見積もりを無料で比べられるサービスがあります。",
}

e = html.escape


def page(p):
    rows = "".join(f"<tr><th>{e(k)}</th><td>{e(v)}</td></tr>" for k, v in p["summary"])
    secs = "".join(f'<section class="box"><h2>{e(h)}</h2><ul>{"".join(f"<li>{e(x)}</li>" for x in items)}</ul></section>' for h, items in p["sections"])
    ld = {"@context": "https://schema.org", "@type": "Article", "headline": p["title"], "description": p["description"],
          "dateModified": CHECKED, "publisher": {"@type": "Organization", "name": "補助金サーチ東京"},
          "mainEntityOfPage": f"{SITE}/hojyo/{p['slug']}"}
    bc = {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "補助金サーチ東京", "item": SITE + "/"},
        {"@type": "ListItem", "position": 2, "name": "住まい・省エネの補助金", "item": SITE + "/hojyo/"},
        {"@type": "ListItem", "position": 3, "name": p["title"]}]}
    kind = p.get("affiliate_kind")
    links = AFFILIATE.get(kind, [])
    pr_note = '<p class="note">※このページにはアフィリエイト広告(PR)が含まれます。</p>' if links else ""
    ad = (f'<section class="box ad"><span class="pr">PR</span><h2>工事の前に見積もりを比べる</h2><p style="font-size:14px">{e(AD_LEAD[kind])}</p>'
          f'<ul>{"".join(f"<li>{x}</li>" for x in links)}</ul>'
          '<p class="note">※広告リンクです。補助金の対象になる機器・工事か、申請に必要な書類を用意してもらえるかは、見積もりのときに業者へ確認してください。</p></section>') if links else ""
    return f"""<!DOCTYPE html>
<html lang="ja"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{e(p['title'])}|{e(p['catch'])}|補助金サーチ東京</title>
<meta name="description" content="{e(p['description'])}">
<link rel="canonical" href="{SITE}/hojyo/{p['slug']}">
<meta property="og:title" content="{e(p['title'])}"><meta property="og:description" content="{e(p['description'])}"><meta property="og:type" content="article"><meta property="og:url" content="{SITE}/hojyo/{p['slug']}.html">
<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>
<script type="application/ld+json">{json.dumps(bc, ensure_ascii=False)}</script>
<style>{CSS}</style></head><body>
<header><a href="/">🔍 補助金サーチ東京</a></header>
<main>
<nav class="crumb"><a href="/">トップ</a> › <a href="/hojyo/">住まい・省エネの補助金</a> › {e(p['title'])}</nav>
<h1>{e(p['title'])}</h1>
<p class="catch">{e(p['catch'])}</p>
{pr_note}
<section class="box"><table>{rows}</table></section>
{secs}
<section class="box"><h2>問い合わせ先</h2><p style="font-size:14px">{e(p['contact'])}</p></section>
{ad}
<section class="box src"><h2>出典・最終確認日</h2>
<p>出典:<a href="{e(p['official_url'])}" target="_blank" rel="noopener">{e(p['official_name'])}({e(p['org'])})</a></p>
<p>最終確認日:{CHECKED}</p>
<p class="note">このページは公式情報をもとに要点をまとめたものです。単価・期間・条件は変更されることがあります。申請の前に、必ず公式ページと手引きで最新の内容を確認してください。</p>
<p style="margin-top:8px"><a class="btn" href="{e(p['official_url'])}" target="_blank" rel="noopener">公式ページを見る →</a></p></section>
</main>
<footer>補助金サーチ東京 | 掲載内容の正確性には注意していますが、最終的な判断は公式情報に基づいて行ってください。</footer>
</body></html>"""


def index_page():
    items = "".join(f'<a href="/hojyo/{p["slug"]}">{e(p["title"])}<span>{e(p["catch"])}</span></a>' for p in PROGRAMS)
    return f"""<!DOCTYPE html>
<html lang="ja"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>東京都の住まい・省エネ補助金まとめ(令和8年度)|補助金サーチ東京</title>
<meta name="description" content="東京都の住まい・省エネに関する令和8年度の補助金を、公式情報をもとにまとめました。蓄電池、窓・ドアの断熱リフォーム、断熱材・高断熱浴槽など。">
<link rel="canonical" href="{SITE}/hojyo/">
<style>{CSS}</style></head><body>
<header><a href="/">🔍 補助金サーチ東京</a></header>
<main><nav class="crumb"><a href="/">トップ</a> › 住まい・省エネの補助金</nav>
<h1>東京都の住まい・省エネ補助金(令和8年度)</h1>
<p class="catch">公式情報を確認してまとめた補助金の一覧です</p>
<section class="box list">{items}</section>
<p class="note">最終確認日:{CHECKED}。申請の前に必ず公式ページで最新の内容を確認してください。</p></main>
<footer>補助金サーチ東京</footer></body></html>"""


for p in PROGRAMS:
    open(os.path.join(PUB, "hojyo", f"{p['slug']}.html"), "w").write(page(p))
open(os.path.join(PUB, "hojyo", "index.html"), "w").write(index_page())
urls = [SITE + "/", SITE + "/hojyo/"] + [f"{SITE}/hojyo/{p['slug']}" for p in PROGRAMS]
urls.append(SITE + "/business/hito-ga-torenai")  # 手書きの事業者向けページ
sm = ('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' +
    "".join(f"  <url><loc>{u}</loc><lastmod>{CHECKED}</lastmod></url>\n" for u in urls) + "</urlset>\n")
open(os.path.join(PUB, "sitemap.xml"), "w").write(sm)
open(os.path.join(PUB, "robots.txt"), "w").write(f"User-agent: *\nAllow: /\nSitemap: {SITE}/sitemap.xml\n")
print("生成:", len(PROGRAMS), "ページ + 一覧 + sitemap.xml + robots.txt")

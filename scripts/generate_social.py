#!/usr/bin/env python3
"""
毎日実行: SNS投稿コンテンツを自動生成
X(Twitter)/Bluesky/Threads/Pinterest用
"""
import json
import os
from datetime import datetime, timezone, timedelta
from pathlib import Path

JST = timezone(timedelta(hours=9))
today = datetime.now(JST)
day_of_year = today.timetuple().tm_yday
date_str = today.strftime("%Y-%m-%d")

BASE = "https://entrynavi.github.io/cryptogate"

# ========== 投稿テンプレート ==========
# 人間味のある自然な文体で統一

EXCHANGE_POSTS = [
    # --- MEXC ---
    f"""正直MEXCの手数料やばい。メイカー0%って何？笑

取扱通貨2700種超えてるから、まだ誰も知らないコインとか普通に買える。草コイン掘るなら一択かも

→ {BASE}/mexc/

#MEXC #仮想通貨""",

    f"""海外取引所どこ使えばいい？ってよく聞かれるけど、とりあえずMEXCで間違いない

・手数料が安い（メイカー0%）
・通貨めちゃくちゃ多い
・日本語対応してる

→ {BASE}/mexc/""",

    f"""MEXCの何がいいって、上場スピードが異常に早いこと。話題になったコインが即買えるのはMEXCくらい

手数料0%だしとりあえず口座作っといて損はない

→ {BASE}/mexc/""",

    # --- Bitget ---
    f"""自分でチャート分析する自信ない人、Bitgetのコピトレ使ってみ？

プロトレーダーの売買を自動でコピーできる。寝てる間にトレードされてるの面白い

→ {BASE}/bitget/

#Bitget #コピートレード""",

    f"""Bitgetのコピトレ、利用者数世界一らしい。実際使ってみると分かるけど、トレーダーの成績見て選ぶだけだから楽すぎる

→ {BASE}/bitget/""",

    # --- Coincheck ---
    f"""仮想通貨始めたいけど怖い、って人はCoincheckからでいいと思う

金融庁にちゃんと登録されてるし、500円から買えるし、アプリもシンプル

紹介で1500円もらえるから実質ノーリスクで始められる

→ {BASE}/coincheck/

#Coincheck""",

    f"""Coincheckの紹介キャンペーンまだやってた。口座作るだけで1500円分のBTCもらえる

→ {BASE}/coincheck/""",

    # --- Binance Japan ---
    f"""Binance Japan、世界最大の取引所が日本で使えるのは普通にでかい。金融庁登録済みだから安心感ある

→ {BASE}/binance-japan/""",

    # --- Hyperliquid ---
    f"""Hyperliquid触ったことない人、そろそろ触っといた方がいいかも

DEXなのにCEXみたいにサクサク動く。ガス代0。オーダーブック型。しかもエアドロの期待値がまだ残ってる

→ {BASE}/hyperliquid/

#Hyperliquid #エアドロップ""",

    f"""Hyperliquidがなぜ話題かって、前回のエアドロで数百万円分もらった人がゴロゴロいるから

次のエアドロに向けて今のうちに触っとくのが吉

→ {BASE}/hyperliquid/""",

    f"""DEXの未来、割とマジでHyperliquidだと思ってる。CEXと遜色ない操作感でオンチェーン取引できるのすごい

→ {BASE}/hyperliquid/""",
]

# --- Tria / Wefi / Ledger / edgeX / SafePal / GMGN / DeBot ---
PRODUCT_POSTS = [
    f"""Triaってウォレット知ってる？Web3のログインがメアドだけでできる。秘密鍵の管理とかいらない

次世代ウォレットって感じ。招待制だからリンク置いとく

→ https://app.tria.so/?accessCode=C77B6U2297""",

    f"""Web3ウォレットで一番簡単なのTriaかも。メールアドレスだけで作れて、シードフレーズとか覚えなくていい

→ https://app.tria.so/?accessCode=C77B6U2297

#Tria #Web3""",

    f"""Wefiっていう新しいDeFiアグリゲーター試してるけど、UIがかなりいい。DeFi初心者でも使いやすい設計

→ https://app.wefi.co/register?ref=m05h1tblot

#Wefi #DeFi""",

    f"""仮想通貨をガチで持つならハードウェアウォレットは必須。取引所に置きっぱなしはリスクでかすぎる

Ledgerが鉄板。オフラインで秘密鍵管理できるから安心感が段違い

→ https://shop.ledger.com/?r=f80cdb813871

#Ledger""",

    f"""取引所がハッキングされたニュース見るたびに思う。自分の資産は自分で守らないとダメ

Ledger持ってない人、まじで一個持っとき

→ https://shop.ledger.com/?r=f80cdb813871""",

    f"""SafePalのハードウェアウォレットも安くて良い。Ledgerほど有名じゃないけど、コスパはこっちの方が上

→ https://www.safepal.com/store/s1?ref=ntu0oth

#SafePal""",

    f"""edgeXってDEX、Hyperliquidと同じオーダーブック型なんだけどUIが洗練されてる。日本語対応もしてる

→ https://pro.edgex.exchange/ja-JP/referral/ZEROMEMO

#edgeX #DEX""",

    f"""GMGNでミームコインのトレンド追うの楽しい。トークンの動きがリアルタイムで見れるから、早乗りしたい人向け

→ https://gmgn.ai/r/MAKAI

#GMGN #ミームコイン""",

    f"""DeBotのAIボット、自動でDeFi運用してくれるらしい。まだ新しいけど面白そうだから触ってみてる

→ https://inv.debot.ai/r/294452?lang=ja

#DeBot #AI""",
]

EDUCATION_POSTS = [
    f"""仮想通貨の税金、確定申告サボると普通に追徴課税くるからね。利益出た人はちゃんと申告しよう

計算方法とか節税テクニックまとめた
→ {BASE}/trending/tax-crypto-japan/""",

    f"""シードフレーズスクショで保存してる人、今すぐやめた方がいい。スマホ乗っ取られたら全部持ってかれる

正しい管理方法はこれ
→ {BASE}/trending/seed-phrase/""",

    f"""ETHのガス代高すぎ問題、L2使えばほぼ解決する。ArbitrumとかOptimismとか。知らないと損してるよ

→ {BASE}/trending/gas-fee-guide/""",

    f"""DeFiで年利10%超え普通にあるけど、その分リスクもある。ラグプルとかハッキングとか

始める前にリスクは理解しとこう
→ {BASE}/trending/defi-toha/""",

    f"""ステーキングって要は通貨預けて利息もらう感じ。銀行の100倍くらい利率いい

始め方まとめてある
→ {BASE}/trending/staking-guide/""",

    f"""ウォレットを取引所に置きっぱなしにしてる人多いけど、取引所がハッキングされたら終わりだからね

自分のウォレット持とう
→ {BASE}/trending/wallet-erabikata/""",

    f"""仮想通貨の始め方、難しく考えすぎてる人多い

1. 取引所で口座作る（5分）
2. 日本円入れる
3. 好きなコイン買う

これだけ
→ {BASE}/hajimekata/""",

    f"""取引所選びで迷ってる人向けに比較表作った。手数料・通貨数・セキュリティ全部まとめてある

→ {BASE}/ranking/""",
]

# ========== 日替わり選択 ==========
all_posts = EXCHANGE_POSTS + PRODUCT_POSTS + EDUCATION_POSTS
weekday = today.weekday()

if weekday in (0, 2, 4):  # Mon, Wed, Fri
    pool = EXCHANGE_POSTS + PRODUCT_POSTS
    post_type = "promo"
else:
    pool = EDUCATION_POSTS + PRODUCT_POSTS
    post_type = "education"

idx = (day_of_year * 7 + weekday) % len(pool)
post_text = pool[idx]

# ========== 出力 ==========
social_dir = Path("social")
social_dir.mkdir(exist_ok=True)

today_file = social_dir / f"{date_str}.txt"
today_file.write_text(post_text, encoding="utf-8")

(social_dir / "latest.txt").write_text(post_text, encoding="utf-8")

meta = {
    "date": date_str,
    "type": post_type,
    "char_count": len(post_text),
}
(social_dir / f"{date_str}.json").write_text(
    json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8"
)

# 週間スケジュール
schedule = []
for i in range(7):
    d = today + timedelta(days=i)
    wd = d.weekday()
    day_name = ["月", "火", "水", "木", "金", "土", "日"][wd]
    ct = "プロモ" if wd in (0, 2, 4) else "教育/プロダクト"
    schedule.append(f"{d.strftime('%-m/%-d')}({day_name}) {ct}")

(social_dir / "schedule.txt").write_text(
    "今週のスケジュール\n" + "\n".join(schedule) + "\n",
    encoding="utf-8",
)

print(f"✅ SNS content: {date_str} ({post_type})")
print(f"📏 {len(post_text)} chars")

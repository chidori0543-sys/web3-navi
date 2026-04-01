#!/usr/bin/env python3
"""
毎日実行: SNS投稿コンテンツを自動生成
X(Twitter)/Bluesky/Threads/Pinterest用
ですます調 + 初心者向け + 画像対応
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

# 投稿に添付する画像（imgディレクトリ内のファイル名）
# post_bluesky.py がこの情報を使って画像を添付する
IMAGES = {
    "ranking": "img/pin-ranking.png",
    "hyperliquid": "img/pin-hyperliquid.png",
    "wallet": "img/pin-wallet.png",
    "hajimekata": "img/pin-hajimekata.png",
    "defi": "img/pin-defi.png",
}

# ========== 投稿テンプレート ==========
# ですます調 + 初心者向けのわかりやすい解説
# 各投稿は (text, image_key or None) のタプル

EXCHANGE_POSTS = [
    # --- MEXC ---
    (f"""MEXCという海外取引所をご存じですか？

取引手数料がメイカー0%で、取扱通貨は2,700種類以上あります。まだ日本では知られていない通貨も多く取り扱っていて、早めに見つけたい方にはおすすめです。

詳しくはこちら
{BASE}/mexc/

#MEXC #仮想通貨 #取引所""", "ranking"),

    (f"""「海外取引所ってどこを使えばいいの？」とよく聞かれます。

迷ったらMEXCがおすすめです。理由はシンプルで、手数料が安い・通貨が多い・日本語に対応しているからです。

始め方はこちらにまとめています
{BASE}/mexc/

#MEXC""", None),

    (f"""MEXCの特徴のひとつが、新しい通貨の上場スピードです。話題になったコインをすぐに取引できるので、情報を追っている方には便利な取引所です。

{BASE}/mexc/""", None),

    # --- Bitget ---
    (f"""「自分でチャートを分析するのは難しい…」という方には、Bitgetのコピートレードがおすすめです。

プロのトレーダーの売買を自動でコピーできる機能で、初心者の方でも始めやすい仕組みになっています。

詳しくはこちら
{BASE}/bitget/

#Bitget #コピートレード""", "ranking"),

    (f"""Bitgetのコピートレードは利用者数が世界トップクラスです。

成績の良いトレーダーを選ぶだけなので、取引の経験が少ない方でも始めやすいのが特徴です。

{BASE}/bitget/""", None),

    # --- Coincheck ---
    (f"""仮想通貨を始めてみたいけど不安…という方には、Coincheckがおすすめです。

金融庁に登録された国内取引所で、500円から購入できます。アプリも使いやすく、初めての方に人気があります。

今なら紹介で1,500円分のBTCがもらえます
{BASE}/coincheck/

#Coincheck #仮想通貨デビュー""", "ranking"),

    (f"""Coincheckの紹介キャンペーンが実施中です。口座を開設するだけで1,500円分のビットコインがもらえます。

まだ口座をお持ちでない方はこの機会にどうぞ
{BASE}/coincheck/""", None),

    # --- Binance Japan ---
    (f"""世界最大級の取引所Binanceが、日本向けにサービスを提供しています。金融庁に登録されているので、安心して利用できます。

{BASE}/binance-japan/

#BinanceJapan #仮想通貨""", None),

    # --- Hyperliquid ---
    (f"""Hyperliquidという分散型取引所（DEX）が注目されています。

CEX（中央集権型）と同じくらいスムーズに取引でき、ガス代（手数料）は0円です。過去のエアドロップで大きなリターンを得た方も多く、今から触っておく価値があります。

始め方はこちら
{BASE}/hyperliquid/

#Hyperliquid #エアドロップ""", "hyperliquid"),

    (f"""Hyperliquidが話題になっている理由は、前回のエアドロップで数百万円相当を受け取った方がいたからです。

次のエアドロップに向けて、今のうちに使い始めておくのがおすすめです。

{BASE}/hyperliquid/""", "hyperliquid"),

    (f"""分散型取引所（DEX）の中でも、Hyperliquidは操作性が優れています。中央集権型と変わらない使い心地で、すべてオンチェーンで完結します。

{BASE}/hyperliquid/""", None),
]

PRODUCT_POSTS = [
    # --- Tria ---
    (f"""Triaというウォレットをご紹介します。メールアドレスだけでWeb3ウォレットが作れます。

秘密鍵やシードフレーズの管理が不要なので、Web3が初めての方でも安心です。招待制のため、以下のリンクからどうぞ。

https://app.tria.so/?accessCode=C77B6U2297

#Tria #Web3ウォレット""", "wallet"),

    (f"""Web3ウォレットの中で一番簡単に使えるのはTriaかもしれません。

メールアドレスだけで登録でき、シードフレーズを覚える必要がありません。初めてのウォレットにおすすめです。

https://app.tria.so/?accessCode=C77B6U2297""", None),

    # --- Wefi ---
    (f"""WefiというDeFiアグリゲーターが使いやすいです。

複数のDeFiプロトコルをまとめて操作できるので、DeFiを始めたい方にとって便利なツールです。

https://app.wefi.co/register?ref=m05h1tblot

#Wefi #DeFi入門""", "defi"),

    # --- Ledger ---
    (f"""仮想通貨を長期で保有する場合、ハードウェアウォレットの利用をおすすめします。

取引所に預けたままだと、万が一のハッキング時にリスクがあります。Ledgerならオフラインで秘密鍵を管理できるので安心です。

https://shop.ledger.com/?r=f80cdb813871

#Ledger #セキュリティ""", "wallet"),

    (f"""取引所のハッキング事件は毎年のように起きています。ご自身の資産を守るために、ハードウェアウォレットを一つ持っておくことをおすすめします。

Ledgerは世界で最も利用されているハードウェアウォレットです。

https://shop.ledger.com/?r=f80cdb813871""", None),

    # --- SafePal ---
    (f"""Ledgerより手頃な価格のハードウェアウォレットをお探しなら、SafePalもおすすめです。コストパフォーマンスが良く、しっかりとセキュリティを確保できます。

https://www.safepal.com/store/s1?ref=ntu0oth

#SafePal #ウォレット""", "wallet"),

    # --- edgeX ---
    (f"""edgeXという分散型取引所をご紹介します。Hyperliquidと同じオーダーブック型のDEXで、UIが洗練されていて日本語にも対応しています。

https://pro.edgex.exchange/ja-JP/referral/ZEROMEMO

#edgeX #DEX""", None),

    # --- GMGN ---
    (f"""ミームコインのトレンドをリアルタイムで追いたい方にはGMGNが便利です。

トークンの値動きや取引量をすぐに確認できるので、情報収集のツールとしておすすめです。

https://gmgn.ai/r/MAKAI

#GMGN #ミームコイン""", None),

    # --- DeBot ---
    (f"""DeBotはAIを活用したDeFi自動運用ツールです。

まだ新しいサービスですが、自動でDeFiの運用をしてくれるので注目しています。興味のある方はぜひ試してみてください。

https://inv.debot.ai/r/294452?lang=ja

#DeBot #AI運用""", None),
]

EDUCATION_POSTS = [
    (f"""仮想通貨で利益が出た場合、確定申告が必要です。申告しないと追徴課税の対象になることもあります。

計算方法や節税のポイントをこちらにまとめていますので、ぜひご確認ください。
{BASE}/trending/tax-crypto-japan/

#仮想通貨 #確定申告""", None),

    (f"""シードフレーズをスクリーンショットで保存していませんか？

スマートフォンが乗っ取られた場合、資産をすべて失うリスクがあります。安全な管理方法をこちらで解説しています。
{BASE}/trending/seed-phrase/

#セキュリティ #シードフレーズ""", "wallet"),

    (f"""ETHのガス代（手数料）が高いと感じている方は、L2（レイヤー2）を使ってみてください。

ArbitrumやOptimismなどを利用すると、手数料を大幅に抑えることができます。
{BASE}/trending/gas-fee-guide/

#イーサリアム #L2""", None),

    (f"""DeFiでは年利10%以上のリターンが得られることもありますが、その分リスクもあります。

ラグプル（詐欺）やハッキングなどの危険性を理解した上で始めることが大切です。
{BASE}/trending/defi-toha/

#DeFi #リスク管理""", "defi"),

    (f"""ステーキングとは、仮想通貨を預けて報酬を受け取る仕組みです。銀行預金よりも高い利回りが期待できます。

初心者向けの始め方ガイドはこちらです。
{BASE}/trending/staking-guide/

#ステーキング #仮想通貨""", None),

    (f"""仮想通貨を取引所に置きっぱなしにしていませんか？

取引所がハッキングされると、預けていた資産を失う可能性があります。自分専用のウォレットを持つことをおすすめします。
{BASE}/trending/wallet-erabikata/

#ウォレット #セキュリティ""", "wallet"),

    (f"""仮想通貨の始め方は意外とシンプルです。

1. 取引所で口座を開設する（約5分）
2. 日本円を入金する
3. 好きな通貨を購入する

詳しい手順はこちらにまとめています。
{BASE}/hajimekata/

#仮想通貨の始め方""", "hajimekata"),

    (f"""取引所選びで迷っている方のために、手数料・取扱通貨数・セキュリティなどを一覧で比較できる表を作りました。

ぜひ参考にしてみてください。
{BASE}/ranking/

#取引所比較 #仮想通貨""", "ranking"),
]

# ========== 日替わり選択 ==========
weekday = today.weekday()

if weekday in (0, 2, 4):  # Mon, Wed, Fri
    pool = EXCHANGE_POSTS + PRODUCT_POSTS
    post_type = "promo"
else:
    pool = EDUCATION_POSTS + PRODUCT_POSTS
    post_type = "education"

idx = (day_of_year * 7 + weekday) % len(pool)
post_text, image_key = pool[idx]

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
    "image": IMAGES.get(image_key) if image_key else None,
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

print(f"SNS content: {date_str} ({post_type})")
print(f"Length: {len(post_text)} chars")
if image_key:
    print(f"Image: {IMAGES[image_key]}")

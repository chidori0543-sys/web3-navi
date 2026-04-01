#!/usr/bin/env python3
"""
毎日実行: SNS投稿コンテンツを自動生成
X(Twitter)・Instagram用の投稿テキストを social/ に出力
API不要 — 手動投稿 or 外部ツール連携用
"""
import json
import os
from datetime import datetime, timezone, timedelta
from pathlib import Path

JST = timezone(timedelta(hours=9))
today = datetime.now(JST)
day_of_year = today.timetuple().tm_yday
date_str = today.strftime("%Y-%m-%d")
month_day = today.strftime("%m/%d")

BASE = "https://entrynavi.github.io/cryptogate"

# ========== 投稿テンプレートプール ==========
# 各取引所プロモーション（アフィリエイトリンク付き）
EXCHANGE_POSTS = [
    {
        "type": "exchange_promo",
        "exchange": "MEXC",
        "tweets": [
            f"""🔥 MEXCが今アツい理由

✅ 取扱通貨2,700種以上（業界最多）
✅ メイカー手数料0%
✅ 最大200倍レバレッジ

草コイン投資なら間違いなくMEXC🚀

▶ 口座開設はこちら（招待コード付き）
{BASE}/mexc/

#仮想通貨 #MEXC #草コイン #投資""",
            f"""💰 仮想通貨の取引手数料、気にしてる？

MEXCならメイカー手数料が0%🎉
2,700種以上の通貨を最安で取引できる

「手数料で損したくない」人にオススメ☝

▶ {BASE}/mexc/

#MEXC #手数料無料 #仮想通貨取引所""",
            f"""🌏 海外取引所デビューするならMEXC

• 日本語完全対応
• 本人確認なしで即取引OK
• 取扱通貨数No.1

初心者でも5分で始められます⏰

▶ {BASE}/mexc/

#仮想通貨初心者 #MEXC #海外取引所""",
        ],
    },
    {
        "type": "exchange_promo",
        "exchange": "Bitget",
        "tweets": [
            f"""🤖 コピートレードで稼ぐ時代

Bitgetなら
✅ プロトレーダーの取引を自動コピー
✅ コピトレ利用者数 世界No.1
✅ 初心者でもプロと同じ結果

「自分で分析する自信がない」人こそBitget💪

▶ {BASE}/bitget/

#Bitget #コピートレード #仮想通貨""",
            f"""⚡ Bitgetのコピトレが凄すぎる

• 10万人以上のトレーダーから選べる
• 自動で24時間取引
• 利益が出たら手数料を払うだけ

寝てる間にも資産が増える💤💰

▶ {BASE}/bitget/

#Bitget #自動売買 #不労所得""",
        ],
    },
    {
        "type": "exchange_promo",
        "exchange": "Coincheck",
        "tweets": [
            f"""🇯🇵 仮想通貨デビューならCoincheck

✅ 金融庁登録済み（安心）
✅ 500円から購入OK
✅ アプリDL数No.1

🎁 今なら紹介キャンペーンで1,500円もらえる！

▶ {BASE}/coincheck/

#Coincheck #仮想通貨デビュー #初心者""",
            f"""🎁 Coincheck紹介キャンペーン実施中！

口座開設するだけで1,500円分のBTCがもらえる🎉

• 金融庁登録の安心取引所
• 500円からスタートOK
• アプリが超使いやすい

▶ {BASE}/coincheck/

#Coincheck #キャンペーン #ビットコイン無料""",
        ],
    },
    {
        "type": "exchange_promo",
        "exchange": "Binance Japan",
        "tweets": [
            f"""🌐 世界最大の取引所が日本上陸

Binance Japanの魅力
✅ 世界1億人以上が利用
✅ 金融庁登録済み
✅ 高いセキュリティ

世界基準の取引環境を日本円で💴

▶ {BASE}/binance-japan/

#BinanceJapan #バイナンス #仮想通貨""",
        ],
    },
    {
        "type": "exchange_promo",
        "exchange": "Hyperliquid",
        "tweets": [
            f"""🚀 次世代DEX「Hyperliquid」が凄い

• オーダーブック型DEX
• CEX並みの速度
• ガス代ゼロ
• エアドロ期待大

DeFiトレーダーなら要チェック✅

▶ {BASE}/hyperliquid/

#Hyperliquid #DEX #DeFi #エアドロップ""",
        ],
    },
]

# 教育コンテンツ（SEO記事への誘導）
EDUCATION_POSTS = [
    f"""📚 仮想通貨の税金、ちゃんと理解してる？

❌ 知らなかったでは済まされない
✅ 確定申告のやり方
✅ 節税テクニック
✅ 計算ツールの使い方

詳しくはこちら⬇
{BASE}/trending/tax-crypto-japan/

#仮想通貨税金 #確定申告 #節税""",
    f"""🔐 シードフレーズ、安全に管理できてる？

❌ スクショ保存はNG
❌ クラウドに保存もNG
✅ 正しい管理方法を解説

資産を守るために必読⬇
{BASE}/trending/seed-phrase/

#セキュリティ #ウォレット #仮想通貨""",
    f"""⛽ ガス代が高すぎる問題の解決法

✅ 安い時間帯を狙う
✅ Layer2を活用
✅ バッチ処理でまとめる

節約テクニック全公開⬇
{BASE}/trending/gas-fee-guide/

#ガス代 #ETH #節約""",
    f"""🎯 DeFiで年利10%以上？

分散型金融（DeFi）の始め方を解説

✅ 主要プロトコル紹介
✅ リスクと注意点
✅ おすすめの始め方

⬇ 詳しくはこちら
{BASE}/trending/defi-toha/

#DeFi #分散型金融 #利回り""",
    f"""💱 ステーキングで不労所得

仮想通貨を預けるだけで報酬がもらえる

✅ 年利5-20%も可能
✅ 初心者でも簡単
✅ おすすめ通貨と取引所

⬇ 始め方ガイド
{BASE}/trending/staking-guide/

#ステーキング #不労所得 #仮想通貨""",
    f"""📱 仮想通貨ウォレットの選び方

「取引所に置きっぱなし」は危険⚠

✅ ホットvsコールドの違い
✅ 用途別おすすめ
✅ 安全な使い方

⬇ 比較ガイド
{BASE}/trending/wallet-erabikata/

#ウォレット #セキュリティ #仮想通貨""",
    f"""🚀 仮想通貨の始め方【完全ガイド】

1⃣ 取引所を選ぶ
2⃣ 口座開設（最短5分）
3⃣ 日本円を入金
4⃣ 好きな通貨を購入

初心者向けに全手順を解説⬇
{BASE}/hajimekata/

#仮想通貨始め方 #初心者 #投資デビュー""",
    f"""🏆 2026年おすすめ取引所ランキング

🥇 MEXC — 手数料最安・通貨数最多
🥈 Bitget — コピトレNo.1
🥉 Coincheck — 初心者に最適

詳しい比較はこちら⬇
{BASE}/ranking/

#取引所ランキング #仮想通貨 #おすすめ""",
]

# ========== 日替わり選択ロジック ==========
# 1週間サイクル: 月水金=取引所プロモ、火木土日=教育コンテンツ
weekday = today.weekday()  # 0=Mon

if weekday in (0, 2, 4):  # Mon, Wed, Fri = exchange promo
    all_exchange_tweets = []
    for ex in EXCHANGE_POSTS:
        for t in ex["tweets"]:
            all_exchange_tweets.append({"exchange": ex["exchange"], "text": t})
    idx = (day_of_year // 2) % len(all_exchange_tweets)
    selected = all_exchange_tweets[idx]
    post_text = selected["text"]
    post_type = f"exchange_promo_{selected['exchange']}"
else:  # Tue, Thu, Sat, Sun = education
    idx = (day_of_year // 2) % len(EDUCATION_POSTS)
    post_text = EDUCATION_POSTS[idx]
    post_type = "education"

# ========== 出力 ==========
social_dir = Path("social")
social_dir.mkdir(exist_ok=True)

# 今日の投稿ファイル
today_file = social_dir / f"{date_str}.txt"
today_file.write_text(post_text, encoding="utf-8")

# latest.txt（常に最新を上書き — 外部ツール連携用）
(social_dir / "latest.txt").write_text(post_text, encoding="utf-8")

# メタデータJSON（分析用）
meta = {
    "date": date_str,
    "type": post_type,
    "char_count": len(post_text),
    "has_link": BASE in post_text,
}
meta_file = social_dir / f"{date_str}.json"
meta_file.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")

# 週間スケジュール生成
schedule = []
for i in range(7):
    d = today + timedelta(days=i)
    wd = d.weekday()
    day_name = ["月", "火", "水", "木", "金", "土", "日"][wd]
    content_type = "取引所プロモ" if wd in (0, 2, 4) else "教育コンテンツ"
    schedule.append(f"{d.strftime('%-m/%-d')}({day_name}) → {content_type}")

schedule_text = "\n".join(schedule)
(social_dir / "schedule.txt").write_text(
    f"📅 今週のSNS投稿スケジュール\n{'='*30}\n{schedule_text}\n",
    encoding="utf-8",
)

print(f"✅ SNS content generated: {date_str}")
print(f"📝 Type: {post_type}")
print(f"📏 Length: {len(post_text)} chars")
print(f"📁 Files: social/{date_str}.txt, social/latest.txt")

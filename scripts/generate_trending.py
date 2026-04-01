#!/usr/bin/env python3
"""
毎日実行: トレンドトピックのミニ記事を自動生成
仮想通貨の基礎知識記事を日替わりで追加してSEOロングテール強化
"""
import os
import json
from datetime import datetime, timezone, timedelta
from pathlib import Path

JST = timezone(timedelta(hours=9))
today = datetime.now(JST)
day_of_year = today.timetuple().tm_yday

# 365日分のトピックプール（ローテーション）
TOPICS = [
    {"slug": "bitcoin-toha", "title": "ビットコイン（BTC）とは？仕組みと特徴をわかりやすく解説", "desc": "ビットコインの基本的な仕組み、マイニング、半減期について初心者向けに解説します。", "kw": "ビットコイン,BTC,仕組み,初心者"},
    {"slug": "ethereum-toha", "title": "イーサリアム（ETH）とは？スマートコントラクトの仕組みを解説", "desc": "イーサリアムの特徴、スマートコントラクト、DeFiとの関係を解説します。", "kw": "イーサリアム,ETH,スマートコントラクト"},
    {"slug": "defi-toha", "title": "DeFi（分散型金融）とは？始め方と注意点", "desc": "DeFiの仕組み、主要プロトコル、リスクと始め方を初心者向けに解説。", "kw": "DeFi,分散型金融,始め方"},
    {"slug": "nft-toha", "title": "NFTとは？仕組み・買い方・将来性を完全解説", "desc": "NFTの基本、購入方法、注意点を初心者にもわかりやすく解説します。", "kw": "NFT,買い方,仕組み"},
    {"slug": "staking-guide", "title": "ステーキングとは？仮想通貨で不労所得を得る方法", "desc": "ステーキングの仕組み、おすすめ通貨、リスクと始め方を解説。", "kw": "ステーキング,不労所得,仮想通貨"},
    {"slug": "airdrop-guide", "title": "エアドロップとは？無料で仮想通貨をもらう方法", "desc": "エアドロップの種類、参加方法、詐欺の見分け方を解説します。", "kw": "エアドロップ,無料,仮想通貨"},
    {"slug": "wallet-erabikata", "title": "仮想通貨ウォレットの選び方｜種類と特徴を比較", "desc": "ホットウォレットとコールドウォレットの違い、おすすめを紹介。", "kw": "ウォレット,選び方,比較"},
    {"slug": "tax-crypto-japan", "title": "仮想通貨の税金｜確定申告のやり方と節税ポイント", "desc": "日本の仮想通貨税制、計算方法、確定申告の手順を解説。", "kw": "仮想通貨,税金,確定申告"},
    {"slug": "leverage-trading", "title": "レバレッジ取引とは？仕組みとリスクを初心者向けに解説", "desc": "レバレッジ取引の基本、ロスカット、おすすめ取引所を紹介。", "kw": "レバレッジ,取引,初心者"},
    {"slug": "memecoin-guide", "title": "ミームコインとは？買い方と注意すべきリスク", "desc": "ミームコインの特徴、人気銘柄、投資リスクを解説します。", "kw": "ミームコイン,買い方,リスク"},
    {"slug": "layer2-guide", "title": "Layer2とは？ブロックチェーンのスケーリング解説", "desc": "Layer2の仕組み、主要プロジェクト、投資機会を解説。", "kw": "Layer2,スケーリング,ブロックチェーン"},
    {"slug": "dex-vs-cex", "title": "DEXとCEXの違い｜どちらを使うべき？", "desc": "分散型取引所と中央集権型取引所の特徴を比較解説。", "kw": "DEX,CEX,違い,取引所"},
    {"slug": "seed-phrase", "title": "シードフレーズとは？安全な管理方法を徹底解説", "desc": "シードフレーズの仕組み、バックアップ方法、よくある失敗を解説。", "kw": "シードフレーズ,管理,セキュリティ"},
    {"slug": "gas-fee-guide", "title": "ガス代とは？ETHのガス代を節約する方法", "desc": "ガス代の仕組み、高い時の対処法、節約テクニックを紹介。", "kw": "ガス代,節約,ETH"},
]

BASE_URL = "https://entrynavi.github.io/cryptogate"

topic = TOPICS[day_of_year % len(TOPICS)]
slug = topic["slug"]
out_dir = Path(f"trending/{slug}")

# 既に存在する場合はスキップ
if out_dir.exists():
    print(f"⏭️  Already exists: {slug}")
    exit(0)

out_dir.mkdir(parents=True, exist_ok=True)
date_str = today.strftime("%Y年%m月%d日")

html = f"""<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{topic['title']} | CryptoGate</title>
  <meta name="description" content="{topic['desc']}">
  <meta name="keywords" content="{topic['kw']}">
  <meta property="og:title" content="{topic['title']} | CryptoGate">
  <meta property="og:description" content="{topic['desc']}">
  <meta property="og:url" content="{BASE_URL}/trending/{slug}/">
  <meta property="og:type" content="article">
  <meta property="og:locale" content="ja_JP">
  <meta property="og:site_name" content="CryptoGate">
  <link rel="canonical" href="{BASE_URL}/trending/{slug}/">
  <link rel="stylesheet" href="../../style.css">
  <link href="https://unpkg.com/aos@2.3.4/dist/aos.css" rel="stylesheet">
</head>
<body>

  <header class="site-header">
    <div class="container">
      <a href="../../" class="logo">CryptoGate<span class="logo-sub">クリプトゲート</span></a>
      <nav class="nav-links">
        <a href="../../">トップ</a>
        <a href="../../ranking/">ランキング</a>
        <a href="../../hajimekata/">始め方</a>
        <a href="../../campaign/">キャンペーン</a>
      </nav>
    </div>
  </header>

  <main class="container article-body">
    <nav class="breadcrumb" data-aos="fade-up">
      <a href="../../">トップ</a> &gt; <a href="../../hajimekata/">始め方</a> &gt; {topic['title']}
    </nav>

    <article>
      <p class="article-meta" data-aos="fade-up">📅 {date_str} · ⏱ 読了 3分</p>
      <h1 data-aos="fade-up">{topic['title']}</h1>

      <p data-aos="fade-up">{topic['desc']}</p>

      <div class="cta-box" data-aos="fade-up">
        <p>仮想通貨の始め方を知りたい方はこちら 👇</p>
        <a href="../../hajimekata/" class="cta-btn">始め方ガイドを読む →</a>
      </div>

      <h2 data-aos="fade-up">まとめ</h2>
      <p data-aos="fade-up">詳しくは各取引所のレビュー記事もご覧ください。</p>

      <div class="cta-box" data-aos="fade-up">
        <p>🏆 取引所ランキングをチェック</p>
        <a href="../../ranking/" class="cta-btn">おすすめランキングを見る →</a>
      </div>
    </article>

    <section class="related-articles" data-aos="fade-up">
      <h3>📚 関連記事</h3>
      <ul>
        <li><a href="../../hajimekata/">仮想通貨の始め方完全ガイド</a></li>
        <li><a href="../../ranking/">取引所おすすめランキング</a></li>
        <li><a href="../../campaign/">最新キャンペーンまとめ</a></li>
      </ul>
    </section>
  </main>

  <footer class="site-footer">
    <div class="container">
      <p>© 2026 CryptoGate｜当サイトにはアフィリエイトリンクが含まれます。投資は自己責任でお願いします。</p>
    </div>
  </footer>

  <script src="https://unpkg.com/aos@2.3.4/dist/aos.js"></script>
  <script>AOS.init({{duration:800, once:true}});</script>
</body>
</html>"""

(out_dir / "index.html").write_text(html, encoding="utf-8")
print(f"✅ Generated: trending/{slug}/index.html — {topic['title']}")

# Update sitemap
sitemap_path = Path("sitemap.xml")
if sitemap_path.exists():
    sitemap = sitemap_path.read_text(encoding="utf-8")
    new_entry = f"""  <url>
    <loc>{BASE_URL}/trending/{slug}/</loc>
    <lastmod>{today.strftime('%Y-%m-%d')}</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.5</priority>
  </url>
</urlset>"""
    sitemap = sitemap.replace("</urlset>", new_entry)
    sitemap_path.write_text(sitemap, encoding="utf-8")
    print(f"✅ Sitemap updated with trending/{slug}/")

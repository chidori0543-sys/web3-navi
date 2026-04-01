#!/usr/bin/env python3
"""
Pinterest自動ピン投稿スクリプト
GitHub Actionsから毎日実行。ピン画像 + タイトル + 説明 + リンクを自動投稿。

環境変数:
  PINTEREST_ACCESS_TOKEN  — OAuth2 アクセストークン
  PINTEREST_BOARD_ID      — 投稿先ボードID

初回セットアップ:
  1. https://developers.pinterest.com/ でアプリ作成
  2. OAuth2 認証フローでアクセストークン取得
  3. GitHub Secrets に PINTEREST_ACCESS_TOKEN, PINTEREST_BOARD_ID を設定
  4. scripts/pinterest_auth.py で認証フローを実行可能
"""
import json
import os
import sys
import urllib.request
from datetime import datetime, timezone, timedelta

ACCESS_TOKEN = os.environ.get("PINTEREST_ACCESS_TOKEN", "")
BOARD_ID = os.environ.get("PINTEREST_BOARD_ID", "")

if not ACCESS_TOKEN or not BOARD_ID:
    print("PINTEREST_ACCESS_TOKEN / PINTEREST_BOARD_ID not set — skipping")
    sys.exit(0)

API_BASE = "https://api.pinterest.com/v5"
BASE_URL = "https://entrynavi.github.io/cryptogate"

# ピンコンテンツ（日替わりで選択）
PINS = [
    {
        "title": "仮想通貨取引所おすすめランキング【2026年最新】",
        "description": "MEXC・Bitget・Coincheck・Binance Japanなど主要取引所を手数料・通貨数・セキュリティで徹底比較。初心者でもわかりやすくまとめています。\n\n#仮想通貨 #取引所比較 #仮想通貨初心者 #MEXC #Bitget #Coincheck",
        "link": f"{BASE_URL}/ranking/",
        "image": "img/pin-ranking.png",
    },
    {
        "title": "Hyperliquid始め方ガイド｜エアドロップ攻略法",
        "description": "KYC不要・ガス代0円の次世代DEX。前回のエアドロップでは数百万円相当を受け取った方も。Season2に向けた始め方を解説します。\n\n#Hyperliquid #エアドロップ #DEX #仮想通貨",
        "link": f"{BASE_URL}/hyperliquid/",
        "image": "img/pin-hyperliquid.png",
    },
    {
        "title": "仮想通貨ウォレットの選び方｜Ledger・SafePal・Tria",
        "description": "ハードウェアウォレットとソフトウェアウォレットの違いを解説。自分に合ったウォレットの選び方をわかりやすくまとめました。\n\n#仮想通貨ウォレット #Ledger #SafePal #Tria #セキュリティ",
        "link": f"{BASE_URL}/trending/wallet-erabikata/",
        "image": "img/pin-wallet.png",
    },
    {
        "title": "仮想通貨の始め方｜初心者向け完全ガイド",
        "description": "口座開設から初めての購入まで、仮想通貨の始め方をステップごとに解説しています。500円から始められるので初心者でも安心です。\n\n#仮想通貨の始め方 #仮想通貨初心者 #投資初心者",
        "link": f"{BASE_URL}/hajimekata/",
        "image": "img/pin-hajimekata.png",
    },
    {
        "title": "DeFi入門ガイド｜仕組みとリスクをわかりやすく解説",
        "description": "DeFi（分散型金融）の基本的な仕組みや始め方、注意すべきリスクをまとめています。ステーキングやレンディングの違いも解説。\n\n#DeFi #分散型金融 #仮想通貨 #ステーキング",
        "link": f"{BASE_URL}/trending/defi-toha/",
        "image": "img/pin-defi.png",
    },
    {
        "title": "MEXC取引所の使い方｜手数料0%の海外取引所",
        "description": "取扱通貨2,700種類以上、メイカー手数料0%のMEXC。口座開設方法から入金・取引の手順まで初心者向けに解説します。\n\n#MEXC #海外取引所 #仮想通貨取引所 #手数料無料",
        "link": f"{BASE_URL}/mexc/",
        "image": "img/pin-ranking.png",
    },
    {
        "title": "Bitgetコピートレードの始め方｜初心者におすすめ",
        "description": "プロトレーダーの売買を自動コピーできるBitget。利用者数世界トップクラスのコピートレード機能の使い方を解説します。\n\n#Bitget #コピートレード #仮想通貨 #自動売買",
        "link": f"{BASE_URL}/bitget/",
        "image": "img/pin-ranking.png",
    },
]

JST = timezone(timedelta(hours=9))
today = datetime.now(JST)
day_of_year = today.timetuple().tm_yday
idx = day_of_year % len(PINS)
pin = PINS[idx]


def pinterest_api(endpoint, data=None, method="GET"):
    """Pinterest API v5 helper"""
    url = f"{API_BASE}/{endpoint}"
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json",
    }
    if data:
        req = urllib.request.Request(url, json.dumps(data).encode(), headers, method=method or "POST")
    else:
        req = urllib.request.Request(url, headers=headers, method=method)

    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read())


def upload_media(image_path):
    """Register media upload with Pinterest, then upload image"""
    # Pinterest v5 pins can use media_source with image_url or image_base64
    import base64
    with open(image_path, "rb") as f:
        image_data = f.read()
    return base64.b64encode(image_data).decode("ascii")


# Create pin
print(f"Creating pin: {pin['title'][:50]}...")

image_b64 = upload_media(pin["image"])

pin_data = {
    "board_id": BOARD_ID,
    "title": pin["title"],
    "description": pin["description"],
    "link": pin["link"],
    "media_source": {
        "source_type": "image_base64",
        "content_type": "image/png",
        "data": image_b64,
    }
}

try:
    result = pinterest_api("pins", pin_data, method="POST")
    print(f"Pin created! ID: {result.get('id', 'N/A')}")
    print(f"Title: {pin['title']}")
    print(f"Link: {pin['link']}")
except urllib.error.HTTPError as e:
    body = e.read().decode("utf-8", errors="replace")
    print(f"Pinterest API error {e.code}: {body}")
    sys.exit(1)

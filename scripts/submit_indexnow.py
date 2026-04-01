#!/usr/bin/env python3
"""
毎日実行: Bing IndexNow にURL送信
主要ページのみ送信（レート制限回避）
"""
import json
import urllib.request

BASE = "https://entrynavi.github.io/cryptogate"
KEY = "a1b2c3d4e5f6"

# 主要ページのみ（毎日全URL送信は不要）
PRIORITY_URLS = [
    f"{BASE}/",
    f"{BASE}/ranking/",
    f"{BASE}/campaign/",
    f"{BASE}/mexc/",
    f"{BASE}/bitget/",
    f"{BASE}/coincheck/",
    f"{BASE}/binance-japan/",
    f"{BASE}/hyperliquid/",
]

payload = json.dumps({
    "host": "entrynavi.github.io",
    "key": KEY,
    "keyLocation": f"{BASE}/{KEY}.txt",
    "urlList": PRIORITY_URLS,
}).encode("utf-8")

req = urllib.request.Request(
    "https://api.indexnow.org/indexnow",
    data=payload,
    headers={"Content-Type": "application/json; charset=utf-8"},
    method="POST",
)

try:
    with urllib.request.urlopen(req, timeout=30) as resp:
        print(f"✅ IndexNow submitted: HTTP {resp.status}")
except Exception as e:
    print(f"⚠️ IndexNow failed (non-critical): {e}")

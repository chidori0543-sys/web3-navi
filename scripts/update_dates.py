#!/usr/bin/env python3
"""
毎日実行: 全HTMLファイルの最終更新日、JSON-LD dateModified、
キャンペーンカウントダウンを自動更新
"""
import re
import glob
from datetime import datetime, timezone, timedelta

JST = timezone(timedelta(hours=9))
today = datetime.now(JST)
today_str = today.strftime("%Y年%m月%d日")
today_iso = today.strftime("%Y-%m-%d")

# キャンペーン期限
CAMPAIGNS = {
    "coincheck": datetime(2026, 4, 6, 16, 59, tzinfo=JST),
    "binance": datetime(2026, 4, 30, 23, 59, tzinfo=JST),
}

updated_files = []

for f in glob.glob("**/*.html", recursive=True):
    with open(f, "r", encoding="utf-8") as fh:
        content = fh.read()

    original = content

    # 1. Update 最終更新: YYYY年MM月DD日
    content = re.sub(
        r"最終更新[:：]\s*\d{4}年\d{1,2}月\d{1,2}日",
        f"最終更新: {today_str}",
        content,
    )

    # 2. Update 【YYYY年M月最新】 in titles
    month_str = f"【{today.year}年{today.month}月最新】"
    content = re.sub(r"【\d{4}年\d{1,2}月最新】", month_str, content)

    # 3. Update JSON-LD dateModified
    content = re.sub(
        r'"dateModified"\s*:\s*"\d{4}-\d{2}-\d{2}"',
        f'"dateModified": "{today_iso}"',
        content,
    )

    # 4. Update campaign countdown days
    for name, deadline in CAMPAIGNS.items():
        if name in f or "campaign" in f or "ranking" in f:
            remaining = (deadline - today).days
            if remaining >= 0:
                # Update patterns like 残りNN日 or あとNN日
                content = re.sub(
                    r"残り\d+日",
                    f"残り{remaining}日",
                    content,
                )

    if content != original:
        with open(f, "w", encoding="utf-8") as fh:
            fh.write(content)
        updated_files.append(f)
        print(f"✅ Updated: {f}")

print(f"\n📅 Date update complete: {today_str}")
print(f"📝 Updated {len(updated_files)} files")

#!/usr/bin/env python3
"""
毎日実行: 全HTMLファイルの「最終更新日」と
キャンペーン残り日数を自動更新するスクリプト
"""
import re
import glob
from datetime import datetime, timezone, timedelta

JST = timezone(timedelta(hours=9))
today = datetime.now(JST)
today_str = today.strftime("%Y年%m月%d日")

# 全HTMLファイルの最終更新表示を更新
for f in glob.glob("**/*.html", recursive=True):
    with open(f, "r", encoding="utf-8") as fh:
        content = fh.read()

    updated = False

    # Update "最終更新: YYYY年MM月DD日" pattern
    new_content = re.sub(
        r"最終更新[:：]\s*\d{4}年\d{1,2}月\d{1,2}日",
        f"最終更新: {today_str}",
        content,
    )
    if new_content != content:
        updated = True
        content = new_content

    # Update "【YYYY年M月最新】" in titles
    month_str = f"【{today.year}年{today.month}月最新】"
    new_content = re.sub(r"【\d{4}年\d{1,2}月最新】", month_str, content)
    if new_content != content:
        updated = True
        content = new_content

    if updated:
        with open(f, "w", encoding="utf-8") as fh:
            fh.write(content)
        print(f"✅ Updated: {f}")

print(f"\n📅 Date update complete: {today_str}")

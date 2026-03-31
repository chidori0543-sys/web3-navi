#!/usr/bin/env python3
"""
毎日実行: sitemap.xmlのlastmod日付を更新
"""
import re
from datetime import datetime, timezone, timedelta

JST = timezone(timedelta(hours=9))
today_iso = datetime.now(JST).strftime("%Y-%m-%d")

with open("sitemap.xml", "r", encoding="utf-8") as f:
    content = f.read()

# Update all lastmod dates to today
content = re.sub(
    r"<lastmod>\d{4}-\d{2}-\d{2}</lastmod>",
    f"<lastmod>{today_iso}</lastmod>",
    content,
)

with open("sitemap.xml", "w", encoding="utf-8") as f:
    f.write(content)

print(f"✅ Sitemap updated: all lastmod → {today_iso}")

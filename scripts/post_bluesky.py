#!/usr/bin/env python3
"""
Bluesky自動投稿スクリプト（リンクカード + 画像対応版）
GitHub Actions から毎日実行、social/latest.txt の内容を投稿
- URLがあればOGPを取得してリンクカード表示
- 画像がある場合はサムネイルとして使用
環境変数: BLUESKY_HANDLE, BLUESKY_APP_PASSWORD
"""
import json
import os
import re
import sys
import urllib.request
from datetime import datetime, timezone, timedelta
from html.parser import HTMLParser

HANDLE = os.environ.get("BLUESKY_HANDLE", "")
APP_PASSWORD = os.environ.get("BLUESKY_APP_PASSWORD", "")

if not HANDLE or not APP_PASSWORD:
    print("BLUESKY_HANDLE / BLUESKY_APP_PASSWORD not set — skipping")
    sys.exit(0)

BASE_URL = "https://bsky.social/xrpc"


def api_call(endpoint, data=None, token=None, raw_body=None, content_type=None):
    """AT Protocol API call"""
    url = f"{BASE_URL}/{endpoint}"
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"

    if raw_body is not None:
        headers["Content-Type"] = content_type or "application/octet-stream"
        req = urllib.request.Request(url, raw_body, headers, method="POST")
    elif data is not None:
        headers["Content-Type"] = "application/json"
        req = urllib.request.Request(url, json.dumps(data).encode(), headers, method="POST")
    else:
        req = urllib.request.Request(url, headers=headers)

    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read())


def parse_facets(text):
    """Parse URLs and hashtags into Bluesky facets with correct UTF-8 byte offsets"""
    facets = []
    text_bytes = text.encode("utf-8")

    for m in re.finditer(r'https?://[^\s\)\]]+', text):
        byte_start = len(text[:m.start()].encode("utf-8"))
        byte_end = len(text[:m.end()].encode("utf-8"))
        try:
            text_bytes[byte_start:byte_end].decode("utf-8")
        except UnicodeDecodeError:
            continue
        facets.append({
            "index": {"byteStart": byte_start, "byteEnd": byte_end},
            "features": [{"$type": "app.bsky.richtext.facet#link", "uri": m.group()}]
        })

    for m in re.finditer(r'#[^\s#\u3000]+', text):
        tag_value = m.group()[1:]
        if not tag_value:
            continue
        byte_start = len(text[:m.start()].encode("utf-8"))
        byte_end = len(text[:m.end()].encode("utf-8"))
        try:
            text_bytes[byte_start:byte_end].decode("utf-8")
        except UnicodeDecodeError:
            continue
        facets.append({
            "index": {"byteStart": byte_start, "byteEnd": byte_end},
            "features": [{"$type": "app.bsky.richtext.facet#tag", "tag": tag_value}]
        })

    return facets


class OGPParser(HTMLParser):
    """Extract Open Graph metadata from HTML"""
    def __init__(self):
        super().__init__()
        self.og = {}
        self.title = ""
        self._in_title = False

    def handle_starttag(self, tag, attrs):
        if tag == "title":
            self._in_title = True
        if tag == "meta":
            attrs_dict = dict(attrs)
            prop = attrs_dict.get("property", "")
            name = attrs_dict.get("name", "")
            content = attrs_dict.get("content", "")
            if prop.startswith("og:"):
                self.og[prop] = content
            elif name == "description" and "og:description" not in self.og:
                self.og["og:description"] = content

    def handle_data(self, data):
        if self._in_title:
            self.title += data

    def handle_endtag(self, tag):
        if tag == "title":
            self._in_title = False


def fetch_ogp(url):
    """Fetch OGP metadata from a URL"""
    try:
        req = urllib.request.Request(url, headers={
            "User-Agent": "Mozilla/5.0 (compatible; CryptoGateBot/1.0)"
        })
        with urllib.request.urlopen(req, timeout=10) as resp:
            html = resp.read().decode("utf-8", errors="replace")

        parser = OGPParser()
        parser.feed(html)

        title = parser.og.get("og:title", parser.title).strip()
        description = parser.og.get("og:description", "").strip()
        image_url = parser.og.get("og:image", "").strip()

        return {"title": title, "description": description, "image": image_url}
    except Exception as e:
        print(f"OGP fetch failed for {url}: {e}")
        return None


def upload_blob(token, data, mime_type="image/png"):
    """Upload a blob to Bluesky"""
    result = api_call(
        "com.atproto.repo.uploadBlob",
        token=token,
        raw_body=data,
        content_type=mime_type,
    )
    return result["blob"]


def download_image(url):
    """Download an image from URL, returns (data, mime_type)"""
    try:
        req = urllib.request.Request(url, headers={
            "User-Agent": "Mozilla/5.0 (compatible; CryptoGateBot/1.0)"
        })
        with urllib.request.urlopen(req, timeout=10) as resp:
            content_type = resp.headers.get("Content-Type", "image/png")
            return resp.read(), content_type.split(";")[0]
    except Exception as e:
        print(f"Image download failed: {e}")
        return None, None


# ===== Main =====

# 1. Login
print(f"Logging in as {HANDLE}...")
session = api_call("com.atproto.server.createSession", {
    "identifier": HANDLE,
    "password": APP_PASSWORD,
})
token = session["accessJwt"]
did = session["did"]
print(f"Logged in: {did}")

# 2. Read today's post
post_file = "social/latest.txt"
if not os.path.exists(post_file):
    print("social/latest.txt not found")
    sys.exit(0)

with open(post_file, "r", encoding="utf-8") as f:
    text = f.read().strip()

if not text:
    print("Empty post content")
    sys.exit(0)

# 3. Check for image in today's metadata
local_image_path = None
JST = timezone(timedelta(hours=9))
date_str = datetime.now(JST).strftime("%Y-%m-%d")
meta_file = f"social/{date_str}.json"
if os.path.exists(meta_file):
    with open(meta_file, "r", encoding="utf-8") as f:
        meta = json.load(f)
    if meta.get("image") and os.path.exists(meta["image"]):
        local_image_path = meta["image"]

# 4. Parse facets
facets = parse_facets(text)

# 5. Truncate to 300 graphemes
if len(text) > 300:
    text = text[:297] + "..."
    max_bytes = len(text.encode("utf-8"))
    facets = [f for f in facets if f["index"]["byteEnd"] <= max_bytes]

# 6. Build embed — prefer link card (external) over image
embed = None
urls = re.findall(r'https?://[^\s\)\]]+', text)
main_url = None
for u in urls:
    if "entrynavi.github.io" in u or "app." in u or "shop." in u or "promote." in u or "share." in u:
        main_url = u
        break
if not main_url and urls:
    main_url = urls[0]

if main_url:
    print(f"Fetching OGP for: {main_url}")
    ogp = fetch_ogp(main_url)
    if ogp and ogp.get("title"):
        external = {
            "uri": main_url,
            "title": ogp["title"][:300],
            "description": ogp.get("description", "")[:1000],
        }
        # Try to get thumbnail: og:image first, then local pin image
        thumb_blob = None
        if ogp.get("image"):
            img_data, mime = download_image(ogp["image"])
            if img_data:
                try:
                    thumb_blob = upload_blob(token, img_data, mime)
                    print("Thumbnail from og:image uploaded")
                except Exception as e:
                    print(f"og:image upload failed: {e}")

        if not thumb_blob and local_image_path:
            try:
                with open(local_image_path, "rb") as f:
                    img_data = f.read()
                thumb_blob = upload_blob(token, img_data, "image/png")
                print(f"Thumbnail from {local_image_path} uploaded")
            except Exception as e:
                print(f"Local image upload failed: {e}")

        if thumb_blob:
            external["thumb"] = thumb_blob

        embed = {
            "$type": "app.bsky.embed.external",
            "external": external,
        }
        print(f"Link card: {ogp['title'][:60]}...")
    else:
        print("OGP not available, trying image embed")

# Fallback to image embed if no link card
if not embed and local_image_path:
    try:
        with open(local_image_path, "rb") as f:
            img_data = f.read()
        blob = upload_blob(token, img_data, "image/png")
        alt_text = text.split("\n")[0][:100]
        embed = {
            "$type": "app.bsky.embed.images",
            "images": [{"alt": alt_text, "image": blob}]
        }
        print("Image embed created")
    except Exception as e:
        print(f"Image upload failed: {e}")

# 7. Build record
now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.000Z")
record = {
    "$type": "app.bsky.feed.post",
    "text": text,
    "createdAt": now,
    "langs": ["ja"],
}
if facets:
    record["facets"] = facets
if embed:
    record["embed"] = embed

# 8. Create post
result = api_call("com.atproto.repo.createRecord", {
    "repo": did,
    "collection": "app.bsky.feed.post",
    "record": record,
}, token=token)

print(f"Posted to Bluesky!")
print(f"Length: {len(text)} chars, Facets: {len(facets)}, Embed: {'yes' if embed else 'no'}")
print(f"URI: {result.get('uri', 'N/A')}")

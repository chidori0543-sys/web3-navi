#!/usr/bin/env python3
"""
Bluesky自動投稿スクリプト（画像対応版）
GitHub Actions から毎日実行、social/latest.txt の内容を投稿
social/{date}.json の image フィールドがあれば画像を添付
環境変数: BLUESKY_HANDLE, BLUESKY_APP_PASSWORD
"""
import json
import os
import re
import sys
import urllib.request
from datetime import datetime, timezone, timedelta

HANDLE = os.environ.get("BLUESKY_HANDLE", "")
APP_PASSWORD = os.environ.get("BLUESKY_APP_PASSWORD", "")

if not HANDLE or not APP_PASSWORD:
    print("BLUESKY_HANDLE / BLUESKY_APP_PASSWORD not set — skipping")
    sys.exit(0)

BASE_URL = "https://bsky.social/xrpc"

def api_call(endpoint, data=None, token=None, raw_body=None, content_type=None):
    """AT Protocol API call helper"""
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

    for m in re.finditer(r'https?://[^\s\)]+', text):
        byte_start = len(text[:m.start()].encode("utf-8"))
        byte_end = len(text[:m.end()].encode("utf-8"))
        # Verify the byte slice decodes correctly
        try:
            text_bytes[byte_start:byte_end].decode("utf-8")
        except UnicodeDecodeError:
            continue
        facets.append({
            "index": {"byteStart": byte_start, "byteEnd": byte_end},
            "features": [{"$type": "app.bsky.richtext.facet#link", "uri": m.group()}]
        })

    for m in re.finditer(r'#[^\s#\u3000]+', text):
        tag_text = m.group()
        tag_value = tag_text[1:]  # remove #
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


def upload_image(token, image_path):
    """Upload image blob to Bluesky, returns blob reference"""
    with open(image_path, "rb") as f:
        image_data = f.read()

    # Determine MIME type
    if image_path.endswith(".png"):
        mime = "image/png"
    elif image_path.endswith(".jpg") or image_path.endswith(".jpeg"):
        mime = "image/jpeg"
    else:
        mime = "image/png"

    result = api_call(
        "com.atproto.repo.uploadBlob",
        token=token,
        raw_body=image_data,
        content_type=mime,
    )
    return result["blob"]


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
image_path = None
JST = timezone(timedelta(hours=9))
date_str = datetime.now(JST).strftime("%Y-%m-%d")
meta_file = f"social/{date_str}.json"
if os.path.exists(meta_file):
    with open(meta_file, "r", encoding="utf-8") as f:
        meta = json.load(f)
    if meta.get("image") and os.path.exists(meta["image"]):
        image_path = meta["image"]
        print(f"Image found: {image_path}")

# 4. Parse facets
facets = parse_facets(text)

# 5. Truncate to 300 graphemes (Bluesky limit)
if len(text) > 300:
    text = text[:297] + "..."
    max_bytes = len(text.encode("utf-8"))
    facets = [f for f in facets if f["index"]["byteEnd"] <= max_bytes]

# 6. Build record
now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.000Z")
record = {
    "$type": "app.bsky.feed.post",
    "text": text,
    "createdAt": now,
    "langs": ["ja"],
}
if facets:
    record["facets"] = facets

# 7. Upload and embed image if available
if image_path:
    try:
        blob = upload_image(token, image_path)
        # Extract alt text from the first line of the post
        alt_text = text.split("\n")[0][:100]
        record["embed"] = {
            "$type": "app.bsky.embed.images",
            "images": [{
                "alt": alt_text,
                "image": blob,
            }]
        }
        print(f"Image uploaded and embedded")
    except Exception as e:
        print(f"Image upload failed (posting without image): {e}")

# 8. Create post
result = api_call("com.atproto.repo.createRecord", {
    "repo": did,
    "collection": "app.bsky.feed.post",
    "record": record,
}, token=token)

print(f"Posted to Bluesky!")
print(f"Length: {len(text)} chars, Facets: {len(facets)}")
print(f"URI: {result.get('uri', 'N/A')}")

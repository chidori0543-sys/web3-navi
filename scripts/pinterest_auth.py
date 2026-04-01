#!/usr/bin/env python3
"""
Pinterest OAuth2 認証ヘルパー
初回セットアップ時にローカルで実行してアクセストークンを取得する

使い方:
  1. https://developers.pinterest.com/ でアプリを作成
  2. App ID と App Secret をメモ
  3. このスクリプトを実行:
     python3 scripts/pinterest_auth.py --app-id YOUR_APP_ID --app-secret YOUR_SECRET
  4. ブラウザで認証URLを開いてアプリを承認
  5. リダイレクト先URLのcodeパラメータをコピーして入力
  6. 表示されたアクセストークンをGitHub Secretsに設定
"""
import argparse
import json
import sys
import urllib.request
import urllib.parse

REDIRECT_URI = "https://localhost/"

def main():
    parser = argparse.ArgumentParser(description="Pinterest OAuth2 認証")
    parser.add_argument("--app-id", required=True, help="Pinterest App ID")
    parser.add_argument("--app-secret", required=True, help="Pinterest App Secret")
    parser.add_argument("--code", help="認証コード（省略時は認証URLを表示）")
    args = parser.parse_args()

    if not args.code:
        # Step 1: 認証URLを生成
        params = urllib.parse.urlencode({
            "client_id": args.app_id,
            "redirect_uri": REDIRECT_URI,
            "response_type": "code",
            "scope": "boards:read,boards:write,pins:read,pins:write",
            "state": "cryptogate",
        })
        auth_url = f"https://www.pinterest.com/oauth/?{params}"
        print("\n以下のURLをブラウザで開いてアプリを承認してください:\n")
        print(auth_url)
        print("\n承認後、リダイレクト先のURLから code= の値をコピーして、")
        print("以下のコマンドを実行してください:\n")
        print(f"python3 scripts/pinterest_auth.py --app-id {args.app_id} --app-secret {args.app_secret} --code <CODE>")
        return

    # Step 2: コードをトークンに交換
    import base64
    credentials = base64.b64encode(f"{args.app_id}:{args.app_secret}".encode()).decode()

    data = urllib.parse.urlencode({
        "grant_type": "authorization_code",
        "code": args.code,
        "redirect_uri": REDIRECT_URI,
    }).encode()

    req = urllib.request.Request(
        "https://api.pinterest.com/v5/oauth/token",
        data=data,
        headers={
            "Authorization": f"Basic {credentials}",
            "Content-Type": "application/x-www-form-urlencoded",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            result = json.loads(resp.read())

        print("\n認証成功!\n")
        print(f"Access Token:  {result['access_token']}")
        print(f"Token Type:    {result.get('token_type', 'bearer')}")
        print(f"Expires In:    {result.get('expires_in', 'N/A')} seconds")
        if "refresh_token" in result:
            print(f"Refresh Token: {result['refresh_token']}")
        print(f"\nScope: {result.get('scope', 'N/A')}")
        print("\n--- GitHub Secrets に設定 ---")
        print(f"  PINTEREST_ACCESS_TOKEN = {result['access_token']}")
        print("\n次にボードIDを取得します...")

        # ボード一覧取得
        boards_req = urllib.request.Request(
            "https://api.pinterest.com/v5/boards",
            headers={"Authorization": f"Bearer {result['access_token']}"},
        )
        with urllib.request.urlopen(boards_req, timeout=30) as resp:
            boards = json.loads(resp.read())

        if boards.get("items"):
            print("\nボード一覧:")
            for b in boards["items"]:
                print(f"  {b['id']} : {b['name']}")
            print(f"\n  PINTEREST_BOARD_ID = {boards['items'][0]['id']}  (最初のボード)")
        else:
            print("\nボードが見つかりません。先にPinterestでボードを作成してください。")

    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        print(f"エラー {e.code}: {body}")
        sys.exit(1)


if __name__ == "__main__":
    main()

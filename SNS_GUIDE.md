# CryptoGate SNS運用ガイド

## 🎨 ブランドアセット（img/ に保存済み）

| ファイル | サイズ | 用途 |
|---------|--------|------|
| `img/profile-icon.svg` | 512x512 | プロフィール画像（全SNS共通） |
| `img/profile.svg` | 512x512 | テキスト入りプロフ（note等） |
| `img/banner.svg` | 1500x500 | ヘッダー画像（X / Bluesky） |
| `img/pin-template.svg` | 1000x1500 | Pinterestピン |

※ SVGをPNGに変換: ブラウザで開いてスクショ or Canvaにインポート

---

## 📱 全アカウント一覧

### 1. Bluesky（最優先 ★★★）
- **表示名**: CryptoGate｜仮想通貨ガイド 🔷
- **ハンドル**: `@cryptogate-jp.bsky.social`
- **プロフ画像**: `img/profile-icon.svg`
- **バナー**: `img/banner.svg`
- **自己紹介**:
  ```
  💎 仮想通貨の入口がここにある
  📊 取引所比較・始め方・最新情報を毎日発信
  🏆 MEXC / Bitget / Coincheck 徹底解説
  🔗 entrynavi.github.io/cryptogate
  ```
- **自動投稿**: ✅ GitHub Actionsで毎日自動（構築済み）
- **費用**: 完全無料
- **セットアップ**:
  1. https://bsky.app で登録
  2. 設定 → アプリパスワード → 新規作成
  3. GitHub Settings → Secrets に `BLUESKY_HANDLE` と `BLUESKY_APP_PASSWORD` 登録

---

### 2. X / Twitter（★★★）
- **表示名**: CryptoGate｜仮想通貨ガイド
- **ユーザー名**: `@cryptogate_jp`
- **プロフ画像**: `img/profile-icon.svg`
- **バナー**: `img/banner.svg`
- **自己紹介**:
  ```
  💎 仮想通貨の入口がここにある
  📊 取引所比較ランキング毎月更新
  🏆 MEXC | Bitget | Coincheck 完全ガイド
  🔰 初心者→上級者まで対応
  ⬇ 無料で始める
  ```
- **リンク**: `entrynavi.github.io/cryptogate`
- **自動投稿**: ⚠️ 手動（social/latest.txt をコピペ、1日5秒）
- **費用**: 無料
- **Tips**: 固定ツイートにランキング記事を貼る

---

### 3. Threads（★★☆）
- **表示名**: CryptoGate｜仮想通貨ガイド
- **ユーザー名**: `@cryptogate_jp`（Instagramと共通）
- **プロフ画像**: `img/profile-icon.svg`
- **自己紹介**:
  ```
  💎 仮想通貨の始め方を毎日発信
  📊 取引所比較・手数料・キャンペーン情報
  🔗 プロフリンクから無料ガイドへ
  ```
- **リンク**: `entrynavi.github.io/cryptogate`
- **自動投稿**: ⚠️ 手動（social/latest.txt をコピペ）
- **費用**: 無料
- **Tips**: Instagramアカウント必須。ハッシュタグ少なめ（3-5個）

---

### 4. Pinterest（★★★ — 超おすすめ）
- **表示名**: CryptoGate｜仮想通貨ガイド
- **ユーザー名**: `cryptogatejp`
- **プロフ画像**: `img/profile-icon.svg`
- **自己紹介**:
  ```
  💎 仮想通貨の入口がここにある
  取引所比較・始め方ガイド・手数料比較・キャンペーン情報
  初心者でも5分で始められる完全ガイド
  ```
- **ウェブサイト**: `entrynavi.github.io/cryptogate`（認証バッジ取得可）
- **ボード構成**:
  - 📊 仮想通貨取引所ランキング
  - 🔰 仮想通貨の始め方
  - 💰 キャンペーン・ボーナス情報
  - 📚 仮想通貨の基礎知識
  - 🔐 セキュリティ・ウォレット
- **ピン画像**: `img/pin-template.svg` をベースにCanvaで量産
- **自動投稿**: API無料（ビジネスアカウント + 開発者申請）
- **費用**: 完全無料
- **最大の利点**: ピンの寿命が長い（数ヶ月〜年単位で流入）、直リンク可

---

### 5. note.com（★★☆ — SEO補助）
- **表示名**: CryptoGate｜仮想通貨ガイド
- **ユーザー名**: `cryptogate`
- **プロフ画像**: `img/profile.svg`（テキスト入り）
- **自己紹介**:
  ```
  仮想通貨の取引所比較・始め方を発信しています。
  MEXC、Bitget、Coincheck、Binance Japan、Hyperliquidの
  手数料・キャンペーン・使い方を徹底比較。
  ▶ メインサイト: entrynavi.github.io/cryptogate
  ```
- **投稿頻度**: 週1（ブログ記事を転載 + note独自コンテンツ）
- **費用**: 無料
- **最大の利点**: noteドメインパワーが高くSEO効果あり、被リンク獲得

---

## 📅 日次運用フロー（所要時間: 約10分/日）

| 時間 | 作業 | 自動/手動 |
|------|------|-----------|
| 9:00 | GitHub Actions実行（日付更新+SNSコンテンツ生成+Bluesky投稿） | ✅ 自動 |
| 9:05 | social/latest.txt をXにコピペ投稿 | 🖐 手動（5秒） |
| 9:06 | 同じ内容をThreadsに投稿 | 🖐 手動（5秒） |
| 18:00 | GitHub Actions 2回目実行 | ✅ 自動 |
| 週末 | Pinterestに新ピンを3-5枚投稿 | 🖐 手動（10分） |
| 週末 | noteに記事1本転載 | 🖐 手動（15分） |

---

## 📌 Pinterest運用テクニック

1. **ビジネスアカウント**で登録（分析+API使える）
2. **ウェブサイト認証**する（SEO効果UP）
3. ピンには必ず**ブログ記事へのリンク**を貼る
4. 画像は**縦長（2:3比率）**が最もエンゲージ高い
5. タイトルに**キーワード**を入れる（Pinterest内SEO）
6. 説明文に**ハッシュタグ**を入れる
7. **毎週3-5ピン**を継続投稿（量が重要）

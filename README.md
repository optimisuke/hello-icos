# IBM Cloud Object Storage Python Client

IBM Cloud Object Storage に Python から簡単にアクセスするためのシンプルなクライアントです。

## セットアップ

### 1. 依存関係のインストール

```bash
pip install -r requirements.txt
```

### 2. 環境変数の設定

`.env`ファイルを作成し、以下の情報を設定してください：

```
IBM_API_KEY=your_api_key_here
IBM_RESOURCE_INSTANCE_ID=your_resource_instance_id_here
IBM_ENDPOINT_URL=https://s3.us-south.cloud-object-storage.appdomain.cloud
```

#### 認証情報の取得方法

1. [IBM Cloud Console](https://cloud.ibm.com)にログイン
2. Object Storage サービスを選択
3. 「サービス資格情報」タブをクリック
4. 「新しい資格情報」を作成
5. 作成された資格情報から以下をコピー：
   - `apikey` → `IBM_API_KEY`
   - `resource_instance_id` → `IBM_RESOURCE_INSTANCE_ID`
   - エンドポイント URL は通常 `https://s3.us-south.cloud-object-storage.appdomain.cloud` （リージョンに応じて変更）

## 使用方法

### 基本的な使用

#### 1. シンプルなバケット操作

```bash
python ibm_cos_simple.py
```

最もシンプルなバケット一覧取得とバケット作成のサンプル。

#### 2. 完全な COS マネージャー（推奨）

```bash
python ibm_cos_manager.py
```

バケット一覧、作成、ファイル一覧を含む完全な機能。

#### 3. 直接 HTTP リクエスト

```bash
python ibm_cos_direct.py
```

HTTP リクエストでの基本的なアクセス例。

#### 4. デバッグ用（XML 解析なし）

```bash
python ibm_cos_debug.py
```

正規表現を使ったシンプルな XML 解析例。

#### 5. ファイル操作（アップロード・ダウンロード）

```bash
python ibm_cos_file_operations.py
```

ファイルのアップロード、ダウンロード、読み込み、削除のサンプル。

#### 6. IBM COS SDK を使用したファイル操作（推奨）

```bash
python ibm_cos_sdk.py
```

IBM 専用 SDK を使用したファイル操作のサンプル。最も IBM COS に最適化されており、完全に動作します。

#### 7. boto3を使用したファイル操作（参考）

```bash
python ibm_cos_boto3.py
```

boto3を使用したファイル操作のサンプル。ただし、IBM COSでは認証が複雑なため、通常のHTTPリクエストを推奨します。

### プログラムでの使用

```python
from ibm_cos_manager import IBMCOSManager

# COSマネージャーを初期化
cos = IBMCOSManager()

# バケット一覧を取得
buckets = cos.list_buckets()
print(f"バケット数: {len(buckets)}")

# バケットを作成
if cos.create_bucket("my-new-bucket"):
    print("バケット作成成功")

# ファイル一覧を取得
files = cos.list_objects("my-bucket")
for file in files:
    print(f"ファイル: {file['key']} ({file['size']} bytes)")
```

## ファイル構成

- `ibm_cos_manager.py` - 完全な COS マネージャークラス（推奨）
- `ibm_cos_simple.py` - 最もシンプルなサンプル
- `ibm_cos_direct.py` - 直接 HTTP リクエストのサンプル
- `ibm_cos_debug.py` - XML を正規表現で解析するサンプル
- `ibm_cos_file_operations.py` - ファイル操作のサンプル
- `ibm_cos_sdk.py` - IBM 専用 SDK を使用したファイル操作のサンプル（推奨）
- `ibm_cos_boto3.py` - boto3を使用したファイル操作のサンプル（参考）
- `requirements.txt` - 必要な Python ライブラリ
- `.env` - 環境変数設定ファイル

## 機能

### サポートされている操作

- ✅ バケット一覧取得
- ✅ バケット作成
- ✅ ファイル一覧取得
- ✅ ファイル詳細情報取得
- ✅ ファイルアップロード
- ✅ ファイルダウンロード
- ✅ テキスト読み込み・書き込み
- ✅ ファイル削除

### 認証方式

- IBM Cloud API Key + OAuth 2.0
- IAM トークンの自動取得・管理

## トラブルシューティング

### 環境変数が設定されていない

```
エラー: 環境変数が設定されていません
IBM_API_KEY, IBM_RESOURCE_INSTANCE_ID, IBM_ENDPOINT_URL を .env に設定してください
```

→ `.env`ファイルに正しい認証情報を設定してください。

### バケット作成エラー

```
バケット作成結果: 409
エラー: BucketAlreadyExists
```

→ バケット名が既に存在します。別の名前を使用してください。

### 認証エラー

```
エラー: 401 Unauthorized
```

→ API Key またはリソースインスタンス ID が正しくない可能性があります。

## 技術的な詳細

### 認証フロー

1. IBM Cloud API Key を使用して IAM トークンを取得
2. 取得したトークンを Bearer トークンとして使用
3. `ibm-service-instance-id`ヘッダーを追加してリクエスト

### エンドポイント

- 認証: `https://iam.cloud.ibm.com/identity/token`
- COS: `https://s3.us-south.cloud-object-storage.appdomain.cloud`

### boto3 との違い

このクライアントは標準の HTTP リクエストを使用しています。boto3 で IBM COS にアクセスする場合、AWS 署名と IBM OAuth 認証の競合により複雑になるため、直接 HTTP リクエストを採用しています。

#### boto3 を使用する場合の注意点

- `ibm_cos_boto3.py` は boto3 を使用したサンプルですが、認証が複雑です
- IBM COS では OAuth 認証が必要なため、標準の AWS 認証と競合します
- 実用的な用途では `ibm_cos_file_operations.py` を推奨します

## ライセンス

MIT License

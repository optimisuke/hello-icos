import os
import requests
from dotenv import load_dotenv

# .envファイルから環境変数を読み込み
load_dotenv()

# 必要な環境変数を取得
API_KEY = os.getenv('IBM_API_KEY')
RESOURCE_INSTANCE_ID = os.getenv('IBM_RESOURCE_INSTANCE_ID')
ENDPOINT_URL = os.getenv('IBM_ENDPOINT_URL')

if not API_KEY or not RESOURCE_INSTANCE_ID or not ENDPOINT_URL:
    print("エラー: 環境変数が設定されていません")
    print("IBM_API_KEY, IBM_RESOURCE_INSTANCE_ID, IBM_ENDPOINT_URL を .env に設定してください")
    exit(1)

# IAMトークンを取得
response = requests.post(
    "https://iam.cloud.ibm.com/identity/token",
    headers={"Content-Type": "application/x-www-form-urlencoded"},
    data={
        "grant_type": "urn:ibm:params:oauth:grant-type:apikey",
        "apikey": API_KEY
    }
)
token = response.json()["access_token"]

# ヘッダー設定
headers = {
    'Authorization': f'Bearer {token}',
    'ibm-service-instance-id': RESOURCE_INSTANCE_ID
}

endpoint = ENDPOINT_URL

# バケット一覧を取得
print("=== バケット一覧 ===")
response = requests.get(endpoint, headers=headers)
if response.status_code == 200:
    import re
    bucket_names = re.findall(r'<Name>(.*?)</Name>', response.text)
    for name in bucket_names:
        print(f"- {name}")
else:
    print(f"エラー: {response.status_code}")

# 新しいバケットを作成
from datetime import datetime
timestamp = int(datetime.now().timestamp())
new_bucket = f"test-bucket-{timestamp}"

print(f"\n=== バケット作成: {new_bucket} ===")
response = requests.put(f"{endpoint}/{new_bucket}", headers=headers)
if response.status_code == 200:
    print("作成成功")
else:
    print(f"作成失敗: {response.status_code}")
    if response.text:
        print(response.text[:200])
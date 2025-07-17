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

# 直接HTTPリクエストでバケット一覧を取得
endpoint = ENDPOINT_URL
headers = {
    'Authorization': f'Bearer {token}',
    'ibm-service-instance-id': RESOURCE_INSTANCE_ID
}

# バケット一覧を取得
response = requests.get(endpoint, headers=headers)
print("バケット一覧:")
print(response.text)

# 新しいバケットを作成
bucket_name = "test-bucket-direct"
response = requests.put(f"{endpoint}/{bucket_name}", headers=headers)
print(f"\nバケット作成結果: {response.status_code}")
if response.status_code == 200:
    print(f"バケット '{bucket_name}' を作成しました")
else:
    print(f"エラー: {response.text}")
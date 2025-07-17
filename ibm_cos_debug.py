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

# バケット一覧を取得（生のXMLを表示）
response = requests.get(ENDPOINT_URL, headers=headers)
print("=== 生のXMLレスポンス ===")
print(response.text[:200] + "...")  # 最初の200文字だけ表示

# XMLを解析せずに、単純に文字列検索
xml_text = response.text
if "<Name>" in xml_text:
    print("\n=== バケット名を抽出 ===")
    import re
    bucket_names = re.findall(r'<Name>(.*?)</Name>', xml_text)
    for name in bucket_names:
        print(f"- {name}")
else:
    print("バケットが見つかりません")
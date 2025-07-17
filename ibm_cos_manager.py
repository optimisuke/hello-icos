import os
import requests
import xml.etree.ElementTree as ET
from datetime import datetime
from dotenv import load_dotenv

class IBMCOSManager:
    def __init__(self):
        # .envファイルから環境変数を読み込み
        load_dotenv()
        
        # 必要な環境変数を取得
        api_key = os.getenv('IBM_API_KEY')
        self.service_instance_id = os.getenv('IBM_RESOURCE_INSTANCE_ID')
        self.endpoint = os.getenv('IBM_ENDPOINT_URL')
        
        if not api_key or not self.service_instance_id or not self.endpoint:
            raise ValueError("環境変数が設定されていません: IBM_API_KEY, IBM_RESOURCE_INSTANCE_ID, IBM_ENDPOINT_URL を .env に設定してください")
        
        # IAMトークンを取得
        response = requests.post(
            "https://iam.cloud.ibm.com/identity/token",
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            data={
                "grant_type": "urn:ibm:params:oauth:grant-type:apikey",
                "apikey": api_key
            }
        )
        self.token = response.json()["access_token"]
        
        self.headers = {
            'Authorization': f'Bearer {self.token}',
            'ibm-service-instance-id': self.service_instance_id
        }
    
    def list_buckets(self):
        """バケット一覧を取得"""
        response = requests.get(self.endpoint, headers=self.headers)
        root = ET.fromstring(response.text)
        
        buckets = []
        for bucket in root.find('.//{http://s3.amazonaws.com/doc/2006-03-01/}Buckets'):
            name = bucket.find('.//{http://s3.amazonaws.com/doc/2006-03-01/}Name').text
            date = bucket.find('.//{http://s3.amazonaws.com/doc/2006-03-01/}CreationDate').text
            buckets.append({'name': name, 'created': date})
        
        return buckets
    
    def create_bucket(self, bucket_name):
        """バケットを作成"""
        response = requests.put(f"{self.endpoint}/{bucket_name}", headers=self.headers)
        return response.status_code == 200
    
    def list_objects(self, bucket_name):
        """バケット内のオブジェクト一覧を取得"""
        response = requests.get(f"{self.endpoint}/{bucket_name}", headers=self.headers)
        if response.status_code != 200:
            return []
        
        root = ET.fromstring(response.text)
        objects = []
        for content in root.findall('.//{http://s3.amazonaws.com/doc/2006-03-01/}Contents'):
            key = content.find('.//{http://s3.amazonaws.com/doc/2006-03-01/}Key').text
            size = content.find('.//{http://s3.amazonaws.com/doc/2006-03-01/}Size').text
            modified = content.find('.//{http://s3.amazonaws.com/doc/2006-03-01/}LastModified').text
            objects.append({'key': key, 'size': int(size), 'modified': modified})
        
        return objects

# 使用例
if __name__ == "__main__":
    cos = IBMCOSManager()
    
    # バケット一覧
    print("=== バケット一覧 ===")
    buckets = cos.list_buckets()
    for bucket in buckets:
        print(f"- {bucket['name']} ({bucket['created']})")
    
    # 新しいバケット作成
    timestamp = int(datetime.now().timestamp())
    new_bucket = f"test-bucket-{timestamp}"
    print(f"\n=== バケット作成: {new_bucket} ===")
    if cos.create_bucket(new_bucket):
        print("作成成功")
    else:
        print("作成失敗")
    
    # 各バケットのファイル一覧
    for bucket in buckets:
        print(f"\n=== {bucket['name']} 内のファイル ===")
        objects = cos.list_objects(bucket['name'])
        if objects:
            for obj in objects:
                print(f"- {obj['key']} ({obj['size']} bytes)")
        else:
            print("ファイルなし")
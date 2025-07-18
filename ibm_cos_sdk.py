import os
import json
import ibm_boto3
from ibm_botocore.client import Config
from datetime import datetime
from dotenv import load_dotenv

class IBMCOSSDKClient:
    def __init__(self):
        # .envファイルから環境変数を読み込み
        load_dotenv()
        
        # 必要な環境変数を取得
        self.api_key = os.getenv('IBM_API_KEY')
        self.service_instance_id = os.getenv('IBM_RESOURCE_INSTANCE_ID')
        self.endpoint_url = os.getenv('IBM_ENDPOINT_URL')
        
        if not self.api_key or not self.service_instance_id or not self.endpoint_url:
            raise ValueError("環境変数が設定されていません: IBM_API_KEY, IBM_RESOURCE_INSTANCE_ID, IBM_ENDPOINT_URL を .env に設定してください")
        
        # IBM COS SDKクライアントを作成
        self.cos_client = ibm_boto3.client(
            's3',
            ibm_api_key_id=self.api_key,
            ibm_service_instance_id=self.service_instance_id,
            config=Config(signature_version='oauth'),
            endpoint_url=self.endpoint_url
        )
    
    def list_buckets(self):
        """バケット一覧を取得"""
        try:
            response = self.cos_client.list_buckets()
            return response['Buckets']
        except Exception as e:
            print(f"エラー: バケット一覧の取得に失敗しました: {e}")
            return []
    
    def create_bucket(self, bucket_name):
        """バケットを作成"""
        try:
            self.cos_client.create_bucket(
                Bucket=bucket_name,
                CreateBucketConfiguration={
                    'LocationConstraint': 'us-south'
                }
            )
            print(f"バケット作成成功: {bucket_name}")
            return True
        except Exception as e:
            print(f"エラー: バケット作成に失敗しました: {e}")
            return False
    
    def upload_file(self, bucket_name, file_path, object_key=None):
        """ファイルをアップロード"""
        if not object_key:
            object_key = os.path.basename(file_path)
        
        try:
            self.cos_client.upload_file(file_path, bucket_name, object_key)
            print(f"ファイルアップロード成功: {file_path} → {bucket_name}/{object_key}")
            return True
        except FileNotFoundError:
            print(f"ファイルが見つかりません: {file_path}")
            return False
        except Exception as e:
            print(f"エラー: ファイルアップロードに失敗しました: {e}")
            return False
    
    def upload_text(self, bucket_name, text_content, object_key):
        """テキストを直接アップロード"""
        try:
            self.cos_client.put_object(
                Bucket=bucket_name,
                Key=object_key,
                Body=text_content.encode('utf-8'),
                ContentType='text/plain; charset=utf-8'
            )
            print(f"テキストアップロード成功: {bucket_name}/{object_key}")
            return True
        except Exception as e:
            print(f"エラー: テキストアップロードに失敗しました: {e}")
            return False
    
    def download_file(self, bucket_name, object_key, local_path=None):
        """ファイルをダウンロード"""
        if not local_path:
            local_path = os.path.basename(object_key)
        
        try:
            # ディレクトリが存在しない場合は作成
            local_dir = os.path.dirname(local_path)
            if local_dir:
                os.makedirs(local_dir, exist_ok=True)
            
            self.cos_client.download_file(bucket_name, object_key, local_path)
            print(f"ファイルダウンロード成功: {bucket_name}/{object_key} → {local_path}")
            return True
        except Exception as e:
            print(f"エラー: ファイルダウンロードに失敗しました: {e}")
            return False
    
    def read_text(self, bucket_name, object_key):
        """テキストファイルを読み込み"""
        try:
            response = self.cos_client.get_object(Bucket=bucket_name, Key=object_key)
            text_content = response['Body'].read().decode('utf-8')
            print(f"テキスト読み込み成功: {bucket_name}/{object_key}")
            return text_content
        except Exception as e:
            print(f"エラー: テキスト読み込みに失敗しました: {e}")
            return None
    
    def delete_file(self, bucket_name, object_key):
        """ファイルを削除"""
        try:
            self.cos_client.delete_object(Bucket=bucket_name, Key=object_key)
            print(f"ファイル削除成功: {bucket_name}/{object_key}")
            return True
        except Exception as e:
            print(f"エラー: ファイル削除に失敗しました: {e}")
            return False
    
    def list_objects(self, bucket_name):
        """バケット内のオブジェクト一覧を取得"""
        try:
            response = self.cos_client.list_objects_v2(Bucket=bucket_name)
            objects = []
            for obj in response.get('Contents', []):
                objects.append({
                    'key': obj['Key'],
                    'size': obj['Size'],
                    'modified': obj['LastModified']
                })
            return objects
        except Exception as e:
            print(f"エラー: オブジェクト一覧の取得に失敗しました: {e}")
            return []
    
    def get_object_info(self, bucket_name, object_key):
        """オブジェクトの詳細情報を取得"""
        try:
            response = self.cos_client.head_object(Bucket=bucket_name, Key=object_key)
            return {
                'size': response['ContentLength'],
                'last_modified': response['LastModified'],
                'content_type': response.get('ContentType', 'unknown')
            }
        except Exception as e:
            print(f"エラー: オブジェクト情報の取得に失敗しました: {e}")
            return None

# 使用例
if __name__ == "__main__":
    cos = IBMCOSSDKClient()
    
    # テスト用のバケット名
    test_bucket = "test-bucket-direct"
    
    print("=== IBM COS SDK を使用したファイル操作のサンプル ===")
    
    # 1. バケット一覧を取得
    print("\n1. バケット一覧")
    buckets = cos.list_buckets()
    for bucket in buckets:
        print(f"  - {bucket['Name']} (作成日: {bucket['CreationDate']})")
    
    # 2. テキストファイルを作成してアップロード
    print("\n2. テキストファイルの作成とアップロード")
    sample_text = f"IBM COS SDK を使用したテストファイルです。\n作成時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
    
    # ローカルファイルを作成
    local_file = "sdk_sample.txt"
    with open(local_file, 'w', encoding='utf-8') as f:
        f.write(sample_text)
    
    # ファイルアップロード
    cos.upload_file(test_bucket, local_file, "sdk_samples/sample.txt")
    
    # 3. テキストを直接アップロード
    print("\n3. テキストの直接アップロード")
    direct_text = f"IBM COS SDK で直接アップロードしたテキストです。\n時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
    cos.upload_text(test_bucket, direct_text, "sdk_samples/direct_text.txt")
    
    # 4. オブジェクト一覧を表示
    print("\n4. オブジェクト一覧")
    objects = cos.list_objects(test_bucket)
    for obj in objects:
        if obj['key'].startswith("sdk_samples/"):
            print(f"  - {obj['key']} ({obj['size']} bytes, 更新: {obj['modified']})")
    
    # 5. ファイルを読み込み
    print("\n5. ファイルの読み込み")
    content = cos.read_text(test_bucket, "sdk_samples/sample.txt")
    if content:
        print("読み込み内容:")
        print(content)
    
    # 6. ファイルをダウンロード
    print("\n6. ファイルのダウンロード")
    cos.download_file(test_bucket, "sdk_samples/direct_text.txt", "sdk_downloaded.txt")
    
    # ダウンロードしたファイルの内容を表示
    if os.path.exists("sdk_downloaded.txt"):
        with open("sdk_downloaded.txt", 'r', encoding='utf-8') as f:
            print("ダウンロードしたファイルの内容:")
            print(f.read())
    
    # 7. オブジェクト情報を取得
    print("\n7. オブジェクト情報の取得")
    info = cos.get_object_info(test_bucket, "sdk_samples/sample.txt")
    if info:
        print(f"ファイル情報: サイズ={info['size']} bytes, 更新={info['last_modified']}, タイプ={info['content_type']}")
    
    # 8. JSONファイルのアップロード例
    print("\n8. JSONファイルのアップロード")
    json_data = {
        "name": "IBM COS SDK Test",
        "timestamp": datetime.now().isoformat(),
        "data": [100, 200, 300, 400, 500],
        "method": "ibm-cos-sdk",
        "version": "2.14.2"
    }
    
    json_content = json.dumps(json_data, indent=2, ensure_ascii=False)
    cos.upload_text(test_bucket, json_content, "sdk_samples/data.json")
    
    # JSONファイルを読み込み
    json_text = cos.read_text(test_bucket, "sdk_samples/data.json")
    if json_text:
        loaded_data = json.loads(json_text)
        print(f"JSONデータ: {loaded_data}")
    
    # 9. 新しいバケットを作成（コメントアウト）
    print("\n9. 新しいバケットの作成（コメントアウト）")
    # new_bucket = f"test-bucket-sdk-{int(datetime.now().timestamp())}"
    # cos.create_bucket(new_bucket)
    
    # 10. クリーンアップ（コメントアウト）
    print("\n10. クリーンアップ（実行する場合はコメントアウトを外してください）")
    # cos.delete_file(test_bucket, "sdk_samples/sample.txt")
    # cos.delete_file(test_bucket, "sdk_samples/direct_text.txt")
    # cos.delete_file(test_bucket, "sdk_samples/data.json")
    
    # ローカルファイルの削除
    if os.path.exists(local_file):
        os.remove(local_file)
        print(f"ローカルファイル削除: {local_file}")
    
    if os.path.exists("sdk_downloaded.txt"):
        os.remove("sdk_downloaded.txt")
        print("ダウンロードファイル削除: sdk_downloaded.txt")
    
    print("\n=== IBM COS SDK を使用したファイル操作のサンプル完了 ===")
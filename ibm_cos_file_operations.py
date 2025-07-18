import os
import requests
from datetime import datetime
from dotenv import load_dotenv


class IBMCOSFileOperations:
    def __init__(self):
        # .envファイルから環境変数を読み込み
        load_dotenv()

        # 必要な環境変数を取得
        api_key = os.getenv('IBM_API_KEY')
        self.service_instance_id = os.getenv('IBM_RESOURCE_INSTANCE_ID')
        self.endpoint = os.getenv('IBM_ENDPOINT_URL')

        if not api_key or not self.service_instance_id or not self.endpoint:
            raise ValueError(
                "環境変数が設定されていません: IBM_API_KEY, IBM_RESOURCE_INSTANCE_ID, IBM_ENDPOINT_URL を .env に設定してください")

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

    def upload_file(self, bucket_name, file_path, object_key=None):
        """ファイルをアップロード"""
        if not object_key:
            object_key = os.path.basename(file_path)

        try:
            with open(file_path, 'rb') as file:
                response = requests.put(
                    f"{self.endpoint}/{bucket_name}/{object_key}",
                    headers=self.headers,
                    data=file
                )

            if response.status_code == 200:
                print(
                    f"ファイルアップロード成功: {file_path} → {bucket_name}/{object_key}")
                return True
            else:
                print(
                    f"ファイルアップロード失敗: {response.status_code} - {response.text}")
                return False

        except FileNotFoundError:
            print(f"ファイルが見つかりません: {file_path}")
            return False
        except Exception as e:
            print(f"エラー: {e}")
            return False

    def upload_text(self, bucket_name, text_content, object_key):
        """テキストを直接アップロード"""
        try:
            response = requests.put(
                f"{self.endpoint}/{bucket_name}/{object_key}",
                headers=self.headers,
                data=text_content.encode('utf-8')
            )

            if response.status_code == 200:
                print(f"テキストアップロード成功: {bucket_name}/{object_key}")
                return True
            else:
                print(
                    f"テキストアップロード失敗: {response.status_code} - {response.text}")
                return False

        except Exception as e:
            print(f"エラー: {e}")
            return False

    def download_file(self, bucket_name, object_key, local_path=None):
        """ファイルをダウンロード"""
        if not local_path:
            local_path = os.path.basename(object_key)

        try:
            response = requests.get(
                f"{self.endpoint}/{bucket_name}/{object_key}",
                headers=self.headers
            )

            if response.status_code == 200:
                # ディレクトリが存在しない場合は作成
                local_dir = os.path.dirname(local_path)
                if local_dir:
                    os.makedirs(local_dir, exist_ok=True)

                with open(local_path, 'wb') as file:
                    file.write(response.content)
                print(
                    f"ファイルダウンロード成功: {bucket_name}/{object_key} → {local_path}")
                return True
            else:
                print(
                    f"ファイルダウンロード失敗: {response.status_code} - {response.text}")
                return False

        except Exception as e:
            print(f"エラー: {e}")
            return False

    def read_text(self, bucket_name, object_key):
        """テキストファイルを読み込み"""
        try:
            response = requests.get(
                f"{self.endpoint}/{bucket_name}/{object_key}",
                headers=self.headers
            )

            if response.status_code == 200:
                text_content = response.text
                print(f"テキスト読み込み成功: {bucket_name}/{object_key}")
                return text_content
            else:
                print(f"テキスト読み込み失敗: {response.status_code} - {response.text}")
                return None

        except Exception as e:
            print(f"エラー: {e}")
            return None

    def delete_file(self, bucket_name, object_key):
        """ファイルを削除"""
        try:
            response = requests.delete(
                f"{self.endpoint}/{bucket_name}/{object_key}",
                headers=self.headers
            )

            if response.status_code == 204:
                print(f"ファイル削除成功: {bucket_name}/{object_key}")
                return True
            else:
                print(f"ファイル削除失敗: {response.status_code} - {response.text}")
                return False

        except Exception as e:
            print(f"エラー: {e}")
            return False

    def list_objects(self, bucket_name):
        """バケット内のオブジェクト一覧を取得"""
        try:
            response = requests.get(
                f"{self.endpoint}/{bucket_name}", headers=self.headers)
            if response.status_code == 200:
                import re
                objects = re.findall(r'<Key>(.*?)</Key>', response.text)
                return objects
            else:
                print(f"オブジェクト一覧取得失敗: {response.status_code}")
                return []
        except Exception as e:
            print(f"エラー: {e}")
            return []


# 使用例
if __name__ == "__main__":
    cos = IBMCOSFileOperations()

    # テスト用のバケット名（実際の既存バケット名に変更してください）
    test_bucket = "test-bucket-direct"

    print("=== ファイル操作のサンプル ===")

    # 1. テキストファイルを作成してアップロード
    print("\n1. テキストファイルの作成とアップロード")
    sample_text = f"これはテストファイルです。\n作成時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"

    # ローカルファイルを作成
    local_file = "sample.txt"
    with open(local_file, 'w', encoding='utf-8') as f:
        f.write(sample_text)

    # ファイルアップロード
    cos.upload_file(test_bucket, local_file, "samples/sample.txt")

    # 2. テキストを直接アップロード
    print("\n2. テキストの直接アップロード")
    direct_text = f"直接アップロードしたテキストです。\n時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
    cos.upload_text(test_bucket, direct_text, "samples/direct_text.txt")

    # 3. オブジェクト一覧を表示
    print("\n3. オブジェクト一覧")
    objects = cos.list_objects(test_bucket)
    for obj in objects:
        if obj.startswith("samples/"):
            print(f"  - {obj}")

    # 4. ファイルを読み込み
    print("\n4. ファイルの読み込み")
    content = cos.read_text(test_bucket, "samples/sample.txt")
    if content:
        print("読み込み内容:")
        print(content)

    # 5. ファイルをダウンロード
    print("\n5. ファイルのダウンロード")
    cos.download_file(test_bucket, "samples/direct_text.txt",
                      "downloaded_text.txt")

    # ダウンロードしたファイルの内容を表示
    if os.path.exists("downloaded_text.txt"):
        with open("downloaded_text.txt", 'r', encoding='utf-8') as f:
            print("ダウンロードしたファイルの内容:")
            print(f.read())

    # 6. JSONファイルのアップロード例
    print("\n6. JSONファイルのアップロード")
    import json

    json_data = {
        "name": "IBM COS Test",
        "timestamp": datetime.now().isoformat(),
        "data": [1, 2, 3, 4, 5]
    }

    json_content = json.dumps(json_data, indent=2, ensure_ascii=False)
    cos.upload_text(test_bucket, json_content, "samples/data.json")

    # JSONファイルを読み込み
    json_text = cos.read_text(test_bucket, "samples/data.json")
    if json_text:
        loaded_data = json.loads(json_text)
        print(f"JSONデータ: {loaded_data}")

    # 7. クリーンアップ（コメントアウト）
    print("\n7. クリーンアップ（実行する場合はコメントアウトを外してください）")
    # cos.delete_file(test_bucket, "samples/sample.txt")
    # cos.delete_file(test_bucket, "samples/direct_text.txt")
    # cos.delete_file(test_bucket, "samples/data.json")

    # ローカルファイルの削除
    if os.path.exists(local_file):
        os.remove(local_file)
        print(f"ローカルファイル削除: {local_file}")

    if os.path.exists("downloaded_text.txt"):
        os.remove("downloaded_text.txt")
        print("ダウンロードファイル削除: downloaded_text.txt")

    print("\n=== ファイル操作のサンプル完了 ===")

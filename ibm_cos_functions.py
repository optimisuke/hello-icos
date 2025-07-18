import os
import ibm_boto3
from ibm_botocore.client import Config
from dotenv import load_dotenv

def _get_cos_client():
    """IBM COS クライアントを取得（各関数で共通して使用）"""
    load_dotenv()
    
    api_key = os.getenv('IBM_API_KEY')
    service_instance_id = os.getenv('IBM_RESOURCE_INSTANCE_ID')
    endpoint_url = os.getenv('IBM_ENDPOINT_URL')
    
    if not api_key or not service_instance_id or not endpoint_url:
        raise ValueError("環境変数が設定されていません: IBM_API_KEY, IBM_RESOURCE_INSTANCE_ID, IBM_ENDPOINT_URL")
    
    return ibm_boto3.client(
        's3',
        ibm_api_key_id=api_key,
        ibm_service_instance_id=service_instance_id,
        config=Config(signature_version='oauth'),
        endpoint_url=endpoint_url
    )

def upload_text(bucket_name, text_content, object_key):
    """
    テキストをIBM COSにアップロード
    
    Args:
        bucket_name (str): アップロード先のバケット名
        text_content (str): アップロードするテキスト内容
        object_key (str): オブジェクトキー（ファイル名）
    
    Returns:
        bool: アップロード成功時True、失敗時False
    """
    try:
        cos_client = _get_cos_client()
        
        cos_client.put_object(
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

def download_file(bucket_name):
    """
    指定したバケットから最新のテキストファイルをダウンロードしてテキストを返す
    
    Args:
        bucket_name (str): ダウンロード元のバケット名
    
    Returns:
        str: ダウンロードしたテキスト内容、失敗時はNone
    """
    try:
        cos_client = _get_cos_client()
        
        # オブジェクト一覧を取得
        response = cos_client.list_objects_v2(Bucket=bucket_name)
        
        if 'Contents' not in response:
            print(f"バケット '{bucket_name}' にオブジェクトが見つかりません")
            return None
        
        # テキストファイルを検索して最新のものを取得
        text_objects = []
        for obj in response['Contents']:
            # .txt で終わるファイルまたはtext/plainのものを対象
            if obj['Key'].endswith('.txt') or obj['Key'].endswith('.text'):
                text_objects.append(obj)
        
        if not text_objects:
            print(f"バケット '{bucket_name}' にテキストファイルが見つかりません")
            return None
        
        # 最新のファイルを取得（LastModified順でソート）
        latest_object = max(text_objects, key=lambda x: x['LastModified'])
        object_key = latest_object['Key']
        
        # ファイルをダウンロード
        file_response = cos_client.get_object(Bucket=bucket_name, Key=object_key)
        text_content = file_response['Body'].read().decode('utf-8')
        
        print(f"ファイルダウンロード成功: {bucket_name}/{object_key} (更新日時: {latest_object['LastModified']})")
        return text_content
        
    except Exception as e:
        print(f"エラー: ファイルダウンロードに失敗しました: {e}")
        return None

def list_objects(bucket_name):
    """
    指定したバケット内のオブジェクト一覧を取得
    
    Args:
        bucket_name (str): 一覧を取得するバケット名
    
    Returns:
        list: オブジェクト情報のリスト、失敗時は空のリスト
    """
    try:
        cos_client = _get_cos_client()
        
        response = cos_client.list_objects_v2(Bucket=bucket_name)
        
        objects = []
        for obj in response.get('Contents', []):
            objects.append({
                'key': obj['Key'],
                'size': obj['Size'],
                'last_modified': obj['LastModified'],
                'etag': obj['ETag'].strip('"')
            })
        
        print(f"オブジェクト一覧取得成功: {bucket_name} ({len(objects)}個のオブジェクト)")
        return objects
        
    except Exception as e:
        print(f"エラー: オブジェクト一覧の取得に失敗しました: {e}")
        return []

def list_buckets():
    """
    バケット一覧を取得
    
    Returns:
        list: バケット情報のリスト、失敗時は空のリスト
    """
    try:
        cos_client = _get_cos_client()
        
        response = cos_client.list_buckets()
        
        buckets = []
        for bucket in response['Buckets']:
            buckets.append({
                'name': bucket['Name'],
                'creation_date': bucket['CreationDate']
            })
        
        print(f"バケット一覧取得成功: {len(buckets)}個のバケット")
        return buckets
        
    except Exception as e:
        print(f"エラー: バケット一覧の取得に失敗しました: {e}")
        return []

def delete_object(bucket_name, object_key):
    """
    指定したオブジェクトを削除
    
    Args:
        bucket_name (str): 削除対象のバケット名
        object_key (str): 削除対象のオブジェクトキー
    
    Returns:
        bool: 削除成功時True、失敗時False
    """
    try:
        cos_client = _get_cos_client()
        
        cos_client.delete_object(Bucket=bucket_name, Key=object_key)
        
        print(f"オブジェクト削除成功: {bucket_name}/{object_key}")
        return True
        
    except Exception as e:
        print(f"エラー: オブジェクト削除に失敗しました: {e}")
        return False

# 使用例
if __name__ == "__main__":
    from datetime import datetime
    
    # テスト用のバケット名
    test_bucket = "test-bucket-direct"
    
    print("=== IBM COS 関数形式のサンプル ===")
    
    # 1. バケット一覧を取得
    print("\n1. バケット一覧")
    buckets = list_buckets()
    for bucket in buckets:
        print(f"  - {bucket['name']} (作成日: {bucket['creation_date']})")
    
    # 2. テキストをアップロード
    print("\n2. テキストのアップロード")
    sample_text = f"関数形式でアップロードしたテキストです。\n作成時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
    upload_text(test_bucket, sample_text, "functions/sample1.txt")
    
    # 3. 別のテキストをアップロード（最新テストのため）
    print("\n3. 別のテキストのアップロード")
    sample_text2 = f"2番目のテキストファイルです。\n作成時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
    upload_text(test_bucket, sample_text2, "functions/sample2.txt")
    
    # 4. オブジェクト一覧を取得
    print("\n4. オブジェクト一覧")
    objects = list_objects(test_bucket)
    for obj in objects:
        if obj['key'].startswith("functions/"):
            print(f"  - {obj['key']} ({obj['size']} bytes, 更新: {obj['last_modified']})")
    
    # 5. 最新のテキストファイルをダウンロード
    print("\n5. 最新のテキストファイルをダウンロード")
    downloaded_text = download_file(test_bucket)
    if downloaded_text:
        print("ダウンロードしたテキスト内容:")
        print(downloaded_text)
    
    # 6. JSON形式のテキストもアップロード
    print("\n6. JSON形式のテキストをアップロード")
    import json
    json_data = {
        "name": "関数形式テスト",
        "timestamp": datetime.now().isoformat(),
        "data": [1, 2, 3, 4, 5]
    }
    json_text = json.dumps(json_data, indent=2, ensure_ascii=False)
    upload_text(test_bucket, json_text, "functions/data.txt")
    
    # 7. 再度最新ファイルをダウンロード（JSONファイルが最新になるはず）
    print("\n7. 再度最新のテキストファイルをダウンロード")
    latest_text = download_file(test_bucket)
    if latest_text:
        print("最新のテキスト内容:")
        print(latest_text)
    
    # 8. クリーンアップ（コメントアウト）
    print("\n8. クリーンアップ（実行する場合はコメントアウトを外してください）")
    # delete_object(test_bucket, "functions/sample1.txt")
    # delete_object(test_bucket, "functions/sample2.txt")
    # delete_object(test_bucket, "functions/data.txt")
    
    print("\n=== 関数形式のサンプル完了 ===")
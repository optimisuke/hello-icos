import ibm_boto3
from ibm_botocore.client import Config
from ibm_watsonx_orchestrate.agent_builder.tools import tool, ToolPermission
from ibm_watsonx_orchestrate.run import connections
from ibm_watsonx_orchestrate.client.connections import ConnectionType


CONNECTION_ICOS = 'icos'
CONNECTION_ICOS_HOST = 'host'
CONNECTION_ICOS_APIKEY = 'apikey'
CONNECTION_ICOS_INSTANCE_ID = 'instance_id'


def _get_cos_client():
    """IBM COS クライアントを取得（各関数で共通して使用）"""
    # 接続情報の取得
    icos_connection = connections.key_value(CONNECTION_ICOS)
    api_key = icos_connection[CONNECTION_ICOS_APIKEY]
    service_instance_id = icos_connection[CONNECTION_ICOS_INSTANCE_ID]
    endpoint_url = icos_connection[CONNECTION_ICOS_HOST]

    if not api_key or not service_instance_id or not endpoint_url:
        raise ValueError(
            "接続情報が設定されていません: apikey, instance_id, host")

    return ibm_boto3.client(
        's3',
        ibm_api_key_id=api_key,
        ibm_service_instance_id=service_instance_id,
        config=Config(signature_version='oauth'),
        endpoint_url=endpoint_url
    )


@tool(
    name="upload_text",
    description="テキストをIBM COSにアップロード",
    permission=ToolPermission.ADMIN,
    expected_credentials=[
        {"app_id": CONNECTION_ICOS, "type": ConnectionType.KEY_VALUE}
    ]
)
def upload_text(bucket_name: str, text_content: str) -> bool:
    """
    テキストをIBM COSにアップロード

    :param bucket_name: アップロード先のバケット名
    :param text_content: アップロードするテキスト内容
    :returns: アップロード成功時True、失敗時False
    """
    try:
        cos_client = _get_cos_client()
        object_key = "test.txt"
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


@tool(
    name="download_file",
    description="指定したバケットから最新のテキストファイルをダウンロード",
    permission=ToolPermission.ADMIN,
    expected_credentials=[
        {"app_id": CONNECTION_ICOS, "type": ConnectionType.KEY_VALUE}
    ]
)
def download_file(bucket_name: str) -> str:
    """
    指定したバケットから最新のテキストファイルをダウンロードしてテキストを返す

    :param bucket_name: ダウンロード元のバケット名
    :returns: ダウンロードしたテキスト内容、失敗時はNone
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
        file_response = cos_client.get_object(
            Bucket=bucket_name, Key=object_key)
        text_content = file_response['Body'].read().decode('utf-8')

        print(
            f"ファイルダウンロード成功: {bucket_name}/{object_key} (更新日時: {latest_object['LastModified']})")
        return text_content

    except Exception as e:
        print(f"エラー: ファイルダウンロードに失敗しました: {e}")
        return None


@tool(
    name="list_objects",
    description="指定したバケット内のオブジェクト一覧を取得",
    permission=ToolPermission.ADMIN,
    expected_credentials=[
        {"app_id": CONNECTION_ICOS, "type": ConnectionType.KEY_VALUE}
    ]
)
def list_objects(bucket_name: str) -> list:
    """
    指定したバケット内のオブジェクト一覧を取得

    :param bucket_name: 一覧を取得するバケット名
    :returns: オブジェクト情報のリスト、失敗時は空のリスト
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


@tool(
    name="list_buckets",
    description="バケット一覧を取得",
    permission=ToolPermission.ADMIN,
    expected_credentials=[
        {"app_id": CONNECTION_ICOS, "type": ConnectionType.KEY_VALUE}
    ]
)
def list_buckets() -> list:
    """
    バケット一覧を取得

    :returns: バケット情報のリスト、失敗時は空のリスト
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


@tool(
    name="delete_object",
    description="指定したオブジェクトを削除",
    permission=ToolPermission.ADMIN,
    expected_credentials=[
        {"app_id": CONNECTION_ICOS, "type": ConnectionType.KEY_VALUE}
    ]
)
def delete_object(bucket_name: str, object_key: str) -> bool:
    """
    指定したオブジェクトを削除

    :param bucket_name: 削除対象のバケット名
    :param object_key: 削除対象のオブジェクトキー
    :returns: 削除成功時True、失敗時False
    """
    try:
        cos_client = _get_cos_client()

        cos_client.delete_object(Bucket=bucket_name, Key=object_key)

        print(f"オブジェクト削除成功: {bucket_name}/{object_key}")
        return True

    except Exception as e:
        print(f"エラー: オブジェクト削除に失敗しました: {e}")
        return False

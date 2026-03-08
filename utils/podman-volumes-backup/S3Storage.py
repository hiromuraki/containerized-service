import os
import boto3
from pathlib import Path
from botocore.exceptions import ClientError


class S3Storage:
    def __init__(self) -> None:
        S3_ENDPOINT_URL = os.environ.get("S3_ENDPOINT_URL")
        S3_ACCESS_KEY = os.environ.get("S3_ACCESS_KEY")
        S_3SECRET_KEY = os.environ.get("S3_SECRET_KEY")

        missing_keys = []
        if not S3_ENDPOINT_URL:
            missing_keys.append("S3_ENDPOINT_URL")
        if not S3_ACCESS_KEY:
            missing_keys.append("S3_ACCESS_KEY")
        if not S_3SECRET_KEY:
            missing_keys.append("S3_SECRET_KEY")

        if missing_keys:
            raise ValueError(f"❌ 启动失败：缺少必要的环境变量 -> {', '.join(missing_keys)}")

        self.__s3_client = boto3.client(
            's3',
            endpoint_url=S3_ENDPOINT_URL,
            aws_access_key_id=S3_ACCESS_KEY,
            aws_secret_access_key=S_3SECRET_KEY
        )

    def upload(self, filepath: Path, bucket: str, key: str) -> None:  # pyright: ignore[reportUndefinedVariable]
        self.__s3_client.upload_file(str(filepath), bucket, key)

    def is_available(self) -> bool:
        try:
            self.__s3_client.list_buckets()
            return True
        except Exception as e:
            print(f"❌ S3 服务不可用：{e}")
            return False

    def file_exists(self, bucket: str, key: str) -> bool:
        try:
            self.__s3_client.head_object(Bucket=bucket, Key=key)
            return True
        except ClientError as e:
            if e.response['Error']['Code'] == '404':
                return False
            raise

    def download(self, bucket: str, key: str, download_path: Path) -> None:
        print(f"⬇️ 正在从 S3 拉取: s3://{bucket}/{key} \n   -> 目标地址: {download_path}")
        self.__s3_client.download_file(bucket, key, str(download_path))
        print("✅ 拉取完成！")

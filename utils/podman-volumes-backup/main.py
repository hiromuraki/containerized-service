import os
from pathlib import Path
import sys
import boto3
from datetime import datetime
from podman import PodmanClient


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

    def upload(self, filepath: Path, bucket: str, key: str) -> None:
        self.__s3_client.upload_file(str(filepath), bucket, key)

    def is_available(self) -> bool:
        try:
            self.__s3_client.list_buckets()
            return True
        except Exception as e:
            print(f"❌ S3 服务不可用：{e}")
            return False


S3 = S3Storage()
BUCKET_NAME = "container-volume"


def upload_to_s3(volume_name: str, filepath: Path) -> None:
    """
    将卷备份上传到 S3 存储
    """
    if not filepath.exists():
        print(f"❌ 错误：未找到本地备份文件 '{filepath}'。")
        return

    if not filepath.name.endswith(".tar.gz"):
        print(f"❌ 错误：'{filepath.name}' 不是有效的 .tar.gz 压缩包。")
        return

    # 构造按日期分类的云端路径 (例如: 2026-03-06/db-data_20260306_223000.tar.gz)
    now = datetime.now()
    date_dir = now.strftime("%Y-%m-%d")
    datetime_str = now.strftime("%Y%m%d_%H%M%S")

    # 最终的云端文件名 (Object Key)

    object_name = f"{date_dir}/{volume_name}_{datetime_str}.tar.gz"

    print(f"☁️  正在将 '{filepath.name}' 上传至 S3 ({BUCKET_NAME}/{object_name}) ...")

    try:
        S3.upload(filepath, BUCKET_NAME, object_name)
        print(f"✅ 上传成功！云端路径: {object_name}")
    except Exception as e:
        raise Exception(f"❌ 上传过程中发生意外错误: {e}")


def get_volume_names() -> list[str]:
    """
    获取 Podman 卷名列表
    """
    uid = os.getuid()
    socket_uri = f"unix:///run/user/{uid}/podman/podman.sock"

    try:
        with PodmanClient(base_url=socket_uri) as client:
            if not client.ping():
                raise ConnectionError("Podman API is not responding!")

            volumes = client.volumes.list()
            return [str(vol.name) for vol in volumes]
    except Exception as e:
        print(f"❌ Podman API 连接失败: {e}")
        print("🔧 请确认是否已执行: systemctl --user enable --now podman.socket")
        raise


def backup_podman_volume(volume_name: str, out_file: Path) -> bool:
    """
    将指定的 Podman 卷打包备份到本地文件。
    """
    uid = os.getuid()
    socket_uri = f"unix:///run/user/{uid}/podman/podman.sock"

    out_file.parent.mkdir(parents=True, exist_ok=True)

    backup_dir = str(out_file.parent.absolute())
    backup_filename = out_file.name

    try:
        with PodmanClient(base_url=socket_uri) as client:
            try:
                client.volumes.get(volume_name)
            except Exception:
                print(f"⏭️  跳过: 找不到存储卷 '{volume_name}'")
                return False

            print(f"⏳ 正在拉起临时容器，打包卷 '{volume_name}' ...")

            client.containers.run(
                image="docker.io/library/alpine:latest",
                command=["tar", "-czvf", f"/backup/{backup_filename}", "-C", "/data", "."],
                remove=True,
                volumes={
                    volume_name: {'bind': '/data', 'mode': 'ro'},
                    backup_dir: {'bind': '/backup', 'mode': 'rw'}
                }
            )

            if out_file.exists() and out_file.stat().st_size > 0:
                print(f"📦 备份打包成功！本地路径: {out_file.absolute()}")
                print(f"📊 文件大小: {out_file.stat().st_size / 1024 / 1024:.2f} MB")
                return True
            else:
                print("⚠️  警告：容器执行完毕，但未在预期位置找到备份文件。")
                return False

    except Exception as e:
        raise Exception(f"❌ 备份过程中发生意外错误: {e}")


if __name__ == "__main__":
    print("🚀 开始执行全量 Podman 卷备份任务...")

    if not S3.is_available():
        print("❌ 脚本将退出 (Exit 1) 并等待 Systemd 触发重试。")
        sys.exit(1)

    print("✅ S3 服务运行正常，准备开始备份。")

    for volume_name in get_volume_names():
        out_file = Path(f"./.backups/{volume_name}.tar.gz").absolute()

        try:
            ok = backup_podman_volume(volume_name, out_file)
            if ok:
                upload_to_s3(volume_name, out_file)
                os.remove(out_file)
                print(f"🗑️  已清理本地临时文件: {out_file.name}\n")

        except Exception as e:
            print(f"🚨 处理卷 '{volume_name}' 时发生严重错误: {e}\n")

    print("🎉 所有备份任务执行完毕！")

import os
from pathlib import Path
from datetime import datetime
import subprocess
import sys
from core import TEMP_DIR, check_volume_exists, get_volume_names, S3, BUCKET_NAME


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


def backup_podman_volume(volume_name: str, out_file: Path) -> bool:
    try:
        print(f"⏳ 正在导出并压缩卷 '{volume_name}' ...")

        if not check_volume_exists(volume_name):
            print(f"⏭️  跳过: 找不到存储卷 '{volume_name}'")
            return False

        cmd = f"podman volume export {volume_name} | gzip > {out_file.absolute()}"

        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

        # 校验结果
        if result.returncode == 0 and out_file.exists() and out_file.stat().st_size > 0:
            print(f"📦 备份打包成功！本地路径: {out_file.absolute()}")
            print(f"📊 文件大小: {out_file.stat().st_size / 1024 / 1024:.2f} MB")
            return True
        else:
            # 如果出错，捕获并打印 stderr
            print(f"❌ 备份失败: {result.stderr}")
            return False
    except Exception as e:
        raise Exception(f"❌ 备份过程中发生意外错误: {e}")


def backup():
    print("🚀 开始执行全量 Podman 卷备份任务...")

    for volume_name in get_volume_names():
        out_file = (Path(TEMP_DIR / f"{volume_name}.tar.gz")).absolute()

        try:
            ok = backup_podman_volume(volume_name, out_file)
            if ok:
                upload_to_s3(volume_name, out_file)
                os.remove(out_file)
                print(f"🗑️  已清理本地临时文件: {out_file.name}\n")

        except Exception as e:
            print(f"🚨 处理卷 '{volume_name}' 时发生严重错误: {e}\n")

    print("🎉 所有备份任务执行完毕！")

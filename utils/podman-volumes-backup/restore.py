from S3Storage import S3Storage
from core import run_command, check_volume_exists, TEMP_DIR, BUCKET_NAME


def restore(target_volume: str, source_key: str):
    # 设定本地临时下载目录
    local_tar_path = TEMP_DIR / source_key.replace("/", "_")

    try:
        if check_volume_exists(target_volume):
            confirm = input(f"⚠️  警告: 卷 '{target_volume}' 已存在。是否删除并重新创建以进行恢复? (y/N): ")
            if confirm.lower() == 'y':
                print(f"🔥 正在删除旧卷 '{target_volume}'...")
                if not run_command(["podman", "volume", "rm", "-f", target_volume]):
                    print("❌ 无法删除现有卷，恢复中止。")
                    return
            else:
                print("🚫 用户取消操作，恢复中止。")
                return

        # 1. 初始化存储引擎
        s3 = S3Storage()
        if not s3.is_available():
            return

        # 2. 存在性校验
        print(f"🔍 检查云端文件: s3://{BUCKET_NAME}/{source_key}")
        if not s3.file_exists(BUCKET_NAME, source_key):
            print(f"❌ 致命错误：云端不存在该备份文件，恢复中止！")
            return

        # 3. 执行拉取
        s3.download(BUCKET_NAME, source_key, local_tar_path)

        # 4. 驱动 Podman 创建卷
        # 此时已经确认卷不存在或已被删除
        if not run_command(["podman", "volume", "create", target_volume]):
            return

        # 5. 驱动 Podman 导入数据
        if not run_command(["podman", "volume", "import", target_volume, str(local_tar_path)]):
            print(f"⚠️ 卷 '{target_volume}' 已创建，但数据导入失败，请检查压缩包格式。")
            return

        print(f"\n🎉 卷 '{target_volume}' 已成功从云端备份恢复。")

    finally:
        # 6. 扫除缓存
        if local_tar_path.exists():
            local_tar_path.unlink()
            print(f"🧹 已清理本地临时缓存: {local_tar_path}")

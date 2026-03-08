import argparse
import os
from pathlib import Path
import sys
from restore import restore
from backup import backup
from core import S3, TEMP_DIR


def main():
    # 建立炫酷的 CLI 命令行解析器
    parser = argparse.ArgumentParser(description="PVM (Podman Volume Manager) - 极客专属的卷灾备工具")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # 定义 restore 子命令
    restore_parser = subparsers.add_parser("restore", help="从 S3 恢复 Podman 卷")
    restore_parser.add_argument("volume", help="目标卷的名称 (xxx)")
    restore_parser.add_argument("--from", dest="source", required=True, help="S3 中的源文件名 (yyy.tar.gz)")

    # 定义 backup 子命令
    backup_parser = subparsers.add_parser("backup", help="将 Podman 卷备份至 S3")

    args = parser.parse_args()

    if not S3.is_available():
        print("❌ S3 存储服务不可用，脚本将退出 (Exit 1) 并等待 Systemd 触发重试。")
        sys.exit(1)

    print("✅ S3 服务运行正常")

    os.makedirs(TEMP_DIR, exist_ok=True)
    if args.command == "restore":
        restore(
            target_volume=args.volume,
            source_key=args.source
        )
    elif args.command == "backup":
        backup()


if __name__ == "__main__":
    main()

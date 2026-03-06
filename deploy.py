#!/bin/python3

import sys
import argparse
import subprocess
from pathlib import Path


def reload_systemd_daemon(dry_run: bool = False):
    """执行 systemctl --user daemon-reload"""
    if dry_run:
        print("\n[DRY RUN] Would execute: systemctl --user daemon-reload")
        return

    print("\n--- RELOADING SYSTEMD ---")
    try:
        # check=True 会在命令返回非零退出码时抛出异常
        subprocess.run(["systemctl", "--user", "daemon-reload"], check=True)
        print("Success: Systemd user daemon reloaded.")
    except subprocess.CalledProcessError as e:
        print(f"Error: Failed to reload systemd daemon. {e}")
    except FileNotFoundError:
        print("Error: 'systemctl' command not found. Are you on a Linux system?")


def get_quadlet_files(service_name: str | None) -> list[Path]:
    target_dirs: list[Path] = []
    base_dir = Path.cwd()

    if service_name:
        target_path = base_dir / service_name
        if not target_path.is_dir():
            print(f"Error: Service directory '{service_name}' does not exist.")
            sys.exit(1)
        target_dirs.append(target_path)
    else:
        for item in base_dir.iterdir():
            if item.is_dir() and item.name.startswith('@'):
                target_dirs.append(item)

    if not target_dirs:
        return []

    quadlet_files = []
    for d in target_dirs:
        quadlet_dir = d / "quadlet"
        if not quadlet_dir.is_dir():
            continue

        for file_path in quadlet_dir.iterdir():
            if file_path.is_file():
                quadlet_files.append(file_path.absolute())

    return quadlet_files


def main():
    # 参数解析
    parser = argparse.ArgumentParser(description="Deploy Podman Quadlet files via symlinks.")
    parser.add_argument('--service', type=str, help="Only deploy the specified directory")
    parser.add_argument('--dry-run', action='store_true', help="Preview actions without making actual changes")
    args = parser.parse_args()

    dest_dir = Path.home() / ".config" / "containers" / "systemd"

    # 1. 遍历符合条件的目录
    quadlet_files = get_quadlet_files(args.service)
    if not quadlet_files:
        print("No Quadlet files found")

    # 2. 内部查重：检查所有待部署文件中是否有同名文件
    for k, v in quadlet_files.items():
        print(f"Error: Name collision detected for '{filename}'!")
        print(f" - Conflict 1: {files_to_deploy[filename]}")
        print(f" - Conflict 2: {file_path}")
        print("Deployment aborted.")
        sys.exit(1)

    # 2. 外部查重：检查目标目录中是否已有重名文件并提示 y/n/a
    actions = []  # 记录操作决策，格式: [(source_path, dest_path, action_type)]
    overwrite_all = False

    for filename, src_path in files_to_deploy.items():
        target_path = dest_dir / filename

        # 目标存在（包含已损坏的软链接）
        if target_path.exists() or target_path.is_symlink():
            if overwrite_all:
                actions.append((src_path, target_path, "link"))
            else:
                while True:
                    choice = input(
                        f"File '{filename}' already exists in destination. Overwrite? [y/n/a]: ").strip().lower()
                    if choice == 'y':
                        actions.append((src_path, target_path, "link"))
                        break
                    elif choice == 'n':
                        actions.append((src_path, target_path, "skip"))
                        break
                    elif choice == 'a':
                        overwrite_all = True
                        actions.append((src_path, target_path, "link"))
                        break
                    else:
                        print("Invalid input. Please enter 'y', 'n', or 'a'.")
        else:
            actions.append((src_path, target_path, "link"))

    has_updates = any(a[2] == "link" for a in actions)

    if has_updates:
        reload_systemd_daemon(dry_run=args.dry_run)
    else:
        print("\nNo configuration changes detected. Skipping daemon-reload.")

    # 3. 实际应用或 Dry-run 预览
    if args.dry_run:
        print("\n--- DRY RUN PREVIEW ---")
        for src, dest, action in actions:
            if action == "link":
                if dest.exists() or dest.is_symlink():
                    print(f"[REPLACE] {dest.name} -> {src}")
                else:
                    print(f"[LINK]    {dest.name} -> {src}")
            else:
                print(f"[SKIP]    {dest.name} (already exists)")
        print("\nNo changes were made.")
    else:
        print("\n--- DEPLOYING ---")
        # 确保目标目录存在
        dest_dir.mkdir(parents=True, exist_ok=True)

        for src, dest, action in actions:
            if action == "link":
                try:
                    # 如果已存在文件或软链接，先删除
                    if dest.exists() or dest.is_symlink():
                        dest.unlink()
                    dest.symlink_to(src)
                    print(f"Success: Linked {dest.name}")
                except Exception as e:
                    print(f"Failed: Could not link {dest.name}. Error: {e}")
            else:
                print(f"Skipped: {dest.name}")

        print("\nDeployment finished. Don't forget to run 'systemctl --user daemon-reload'!")


if __name__ == '__main__':
    main()

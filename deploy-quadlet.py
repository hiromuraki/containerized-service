#!/bin/python3

import sys
import argparse
import subprocess
from pathlib import Path
from typing import Literal

DEST_DIR = Path.home() / ".config" / "containers" / "systemd"
QUADLET_FILE_EXTS = set((".container", ".volume", ".network", ".pod", ".kube", ".image"))

type DeploymentAction = tuple[Path, Path, Literal["link", "skip"]]


def is_quadlet_file(path: Path) -> bool:
    return path.suffix in QUADLET_FILE_EXTS


def get_quadlet_files(service_name: str | None) -> list[Path]:
    target_dirs: list[Path] = []
    base_dir = Path.cwd()
    quadlet_files = []

    # 1. 首先：检查根目录 (base_dir) 下的所有 Quadlet 文件
    for item in base_dir.iterdir():
        if item.is_file() and is_quadlet_file(item):
            quadlet_files.append(item.absolute())

    # 2. 确定需要深入扫描的服务子目录
    if service_name:
        target_path = base_dir / service_name
        if not target_path.is_dir():
            print(f"❌ 错误：服务目录 '{service_name}' 不存在。")
            sys.exit(1)
        target_dirs.append(target_path)
    else:
        for item in base_dir.iterdir():
            if item.is_dir() and item.name.startswith('@'):
                target_dirs.append(item)

    # 3. 遍历目标子目录，扫描其内部的 'quadlet' 文件夹
    for target_dir in target_dirs:
        quadlet_dir = target_dir / "quadlet"
        if not quadlet_dir.is_dir():
            continue

        for file_path in quadlet_dir.iterdir():
            if file_path.is_file() and is_quadlet_file(file_path):
                quadlet_files.append(file_path.absolute())

    return quadlet_files


def deploy(actions: list[DeploymentAction]):
    print("\n--- DEPLOYING ---")
    DEST_DIR.mkdir(parents=True, exist_ok=True)

    for src, dest, action in actions:
        if action == "link":
            try:
                if dest.exists() or dest.is_symlink():
                    dest.unlink()
                dest.symlink_to(src)
                print(f"Success: Linked {dest.name}")
            except Exception as e:
                print(f"Failed: Could not link {dest.name}. Error: {e}")
        else:
            print(f"Skipped: {dest.name}")

    print("\nQuadlet files deployment finished.")


def deploy_dry_run(actions: list[DeploymentAction]):
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


def reload_systemd_daemon():
    print("\n--- RELOADING SYSTEMD ---")
    try:
        # check=True 会在命令返回非零退出码时抛出异常
        subprocess.run(["systemctl", "--user", "daemon-reload"], check=True)
        print("Success: Systemd user daemon reloaded.")
    except subprocess.CalledProcessError as e:
        print(f"Error: Failed to reload systemd daemon. {e}")
    except FileNotFoundError:
        print("Error: 'systemctl' command not found. Are you on a Linux system?")


def reload_systemd_daemon_dry_run():
    print("\n[DRY RUN] Would execute: systemctl --user daemon-reload")


def main():
    # 参数解析
    parser = argparse.ArgumentParser(description="Deploy Podman Quadlet files via symlinks.")
    parser.add_argument('--service', type=str, help="Only deploy the specified directory")
    parser.add_argument('--kube-only', action='store_true',
                        help="Only deploy the .kube and its required quadlet files")
    parser.add_argument('--dry-run', action='store_true', help="Preview actions without making actual changes")
    args = parser.parse_args()

    # 1. 遍历符合条件的目录
    quadlet_files = get_quadlet_files(args.service)
    if args.kube_only:
        quadlet_files = [x for x in quadlet_files if x.suffix in (".kube", ".network", ".volume")]

    if not quadlet_files:
        print("No Quadlet files found")
        return
    else:
        print(f"Found {len(quadlet_files)} Quadlet files")

    # 2. 内部查重：检查所有待部署文件中是否有同名文件
    used_filenames: dict[str, Path] = {}
    for file in quadlet_files:
        filename = file.name
        if filename in used_filenames:
            print(f"Error: Name collision detected for '{filename}'!")
            print(f" - Conflict 1: {file}")
            print(f" - Conflict 2: {used_filenames[filename]}")
            print("Deployment aborted.")
            sys.exit(1)
        used_filenames[filename] = file

    # 2. 外部查重：检查目标目录中是否已有重名文件并提示 y/n/a
    # 记录操作决策，格式: [(source_path, dest_path, action_type)]
    actions: list[tuple[Path, Path, Literal["link", "skip"]]] = []
    overwrite_all = False

    for file in quadlet_files:
        filename = file.name
        target_path = DEST_DIR / filename

        # 目标存在（包含已损坏的软链接）
        if target_path.exists() or target_path.is_symlink():
            if overwrite_all:
                actions.append((file, target_path, "link"))
            else:
                while True:
                    choice = input(
                        f"File '{filename}' already exists in destination. Overwrite? [y/n/a]: ").strip().lower()
                    if choice == 'y':
                        actions.append((file, target_path, "link"))
                        break
                    elif choice == 'n':
                        actions.append((file, target_path, "skip"))
                        break
                    elif choice == 'a':
                        overwrite_all = True
                        actions.append((file, target_path, "link"))
                        break
                    else:
                        print("Invalid input. Please enter 'y', 'n', or 'a'.")
        else:
            actions.append((file, target_path, "link"))

    # 3. 实际应用或 Dry-run 预览
    if args.dry_run:
        deploy_dry_run(actions)
    else:
        deploy(actions)

    has_updates = any(a[2] == "link" for a in actions)

    if has_updates:
        if args.dry_run:
            reload_systemd_daemon_dry_run()
        else:
            reload_systemd_daemon()
    else:
        print("\nNo configuration changes detected. Skipping daemon-reload.")


if __name__ == '__main__':
    main()

#!/bin/python3

import os
import sys
import argparse
import subprocess
from pathlib import Path
from typing import Literal
from dataclasses import dataclass

QUADLET_FILE_EXTS = set((".container", ".volume", ".network", ".pod", ".kube", ".image"))


@dataclass
class DeploymentAction:
    source: Path
    dest: Path
    action: Literal["link", "skip"]


class QuadletService:
    QUADLET_TARGET_DIR = Path.home() / ".config/containers/systemd"

    def __init__(self, service_name: str) -> None:
        self.service_name = service_name
        self.__service_dir = Path(os.getcwd()) / f"@{service_name}"

    def deploy(self, kube_mode: bool, dry_run: bool) -> None:
        if not self.__service_dir.exists():
            raise FileNotFoundError(f"❌ 错误：服务目录 '{self.__service_dir.name}' 不存在 ({self.__service_dir})。")

        print(f"⚙️  部署模式: {'Kubernetes 编排 (.kube)' if kube_mode else '原生容器 (.container / .pod)'}")

        # 文件搜集
        link_tasks: list[tuple[Path, Path]] = []
        common_quadlet_dir = self.__service_dir / "common"

        if common_quadlet_dir.exists() and common_quadlet_dir.is_dir():
            for item in common_quadlet_dir.iterdir():
                if item.is_file() and QuadletService.is_quadlet_file(item):
                    link_tasks.append((item.absolute(), QuadletService.QUADLET_TARGET_DIR / item.name))

        if kube_mode:
            kube_file = self.__service_dir / f"{self.service_name}.kube"
            if kube_file.exists() and kube_file.is_file():
                link_tasks.append((kube_file.absolute(), QuadletService.QUADLET_TARGET_DIR / kube_file.name))
            else:
                print(f"⚠️  警告：启用了 Kube 模式，但在预期位置未找到入口文件 '{kube_file.name}'")
        else:
            container_dir = self.__service_dir
            if container_dir.exists() and container_dir.is_dir():
                for item in container_dir.iterdir():
                    if item.is_file() and (item.name.endswith(".container") or item.name.endswith(".pod")):
                        link_tasks.append((item.absolute(), QuadletService.QUADLET_TARGET_DIR / item.name))

        if not link_tasks:
            print("🤷 未找到任何需要部署的配置文件，操作已跳过。")
            return

        # 重名检查
        for _, dest in link_tasks:
            if dest.exists() or dest.is_symlink():
                raise FileExistsError(
                    f"❌ 部署中断：目标路径已被占用 -> {dest.name}\n   (请先清理 ~/.config/containers/systemd/ 下的冲突文件后再试)")

        dest_names = [dest.name for _, dest in link_tasks]
        if len(dest_names) != len(set(dest_names)):
            raise ValueError("❌ 部署中断：本次部署的源文件中存在同名文件，会导致覆盖冲突")

        # 执行
        if dry_run:
            print(f"\n🔍 [Dry Run] 预检模式启动，预计对 '{self.service_name}' 执行以下操作：")
            if not QuadletService.QUADLET_TARGET_DIR.exists():
                print(f"   📁 [创建目录] {QuadletService.QUADLET_TARGET_DIR}")
            for src, dest in link_tasks:
                print(f"   🔗 [创建链接] {dest.name} -> {src.relative_to(Path.cwd())}")
            print("\n✅ 预检通过：文件检查无冲突，未执行任何实际修改。")
            return

        # 实际创建操作
        QuadletService.QUADLET_TARGET_DIR.mkdir(parents=True, exist_ok=True)
        print(f"\n🚀 开始部署 '{self.service_name}' ...")

        for src, dest in link_tasks:
            dest.symlink_to(src)
            print(f"   🔗 已链接: {dest.name}")

        print(f"🎉 部署阶段完成")

    @classmethod
    def is_quadlet_file(cls, path: Path) -> bool:
        return path.suffix in QUADLET_FILE_EXTS


def reload_systemd_daemon(dry_run: bool):
    if dry_run:
        print("✅ [Dry Run] 预检模式跳过执行命令: systemctl --user daemon-reload")
        return

    print("🔄 正在重载 Systemd 用户守护进程 (daemon-reload) ...")
    try:
        # capture_output 可以在失败时抓取具体的报错文本，而不是任由它污染控制台
        subprocess.run(["systemctl", "--user", "daemon-reload"], check=True, capture_output=True, text=True)
        print("✅ Systemd 重载成功！新的 Quadlet 配置已就绪。")
    except subprocess.CalledProcessError as e:
        print(f"❌ 错误: Systemd 重载失败！\n   底层报错: {e.stderr.strip()}")
    except FileNotFoundError:
        print("❌ 错误: 找不到 'systemctl' 命令，请确认当前运行环境为真实的 Linux 系统。")


def main():
    parser = argparse.ArgumentParser(
        description="🚀 优雅地使用软链接管理和部署 Podman Quadlet 服务。",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument('service', type=str, nargs='?', default=None,
                        help="要部署的服务名称 (自动寻找当前目录下的 @<service> 文件夹)")
    parser.add_argument('--kube', action='store_true',
                        help="使用 Kube 模式部署 (自动搜集 .kube 文件)")
    parser.add_argument('--dry-run', action='store_true',
                        help="预检模式 (仅打印执行计划，不进行任何实际更改)")
    args = parser.parse_args()

    if not args.service:
        parser.print_help()
        sys.exit(0)
    
    service_name = args.service[1:] if args.service.startswith("@") else args.service

    try:
        QuadletService(service_name).deploy(kube_mode=args.kube, dry_run=args.dry_run)
        print("-" * 50)
        reload_systemd_daemon(args.dry_run)
    except Exception as e:
        print(f"\n{e}")
        sys.exit(1)


if __name__ == '__main__':
    main()

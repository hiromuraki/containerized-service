import subprocess
from S3Storage import S3Storage
from pathlib import Path

S3 = S3Storage()
BUCKET_NAME = "container-volume"
TEMP_DIR = Path.home() / ".cache/pvm"


def run_command(cmd: list) -> bool:
    print(f"⚙️  执行引擎命令: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"❌ 命令执行失败:\n{result.stderr}")
        return False
    return True


def check_volume_exists(volume_name: str) -> bool:
    """
    检查 Podman 卷是否已存在
    """
    result = subprocess.run(
        ["podman", "volume", "exists", volume_name],
        capture_output=False
    )
    return result.returncode == 0


def get_volume_names() -> list[str]:
    """
    通过 CLI 获取 Podman 卷名列表
    """
    try:
        # 使用 --format "{{.Name}}" 只输出卷名，不带表头
        result = subprocess.run(
            ["podman", "volume", "ls", "--format", "{{.Name}}"],
            capture_output=True,
            text=True,
            check=True
        )

        # 将输出按行拆分，并过滤掉空行
        volume_names = [line.strip() for line in result.stdout.splitlines() if line.strip()]
        return volume_names

    except subprocess.CalledProcessError as e:
        print(f"❌ 获取 Podman 卷列表失败: {e.stderr}")
        # CLI 报错通常意味着 podman 没装或者权限问题
        raise
    except Exception as e:
        print(f"❌ 发生未知错误: {e}")
        raise

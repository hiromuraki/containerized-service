import socket
import sys
import time
import random
import tomllib
from datetime import datetime


def keep_alive(dns_server: str) -> bool:
    try:
        with socket.create_connection((dns_server, 53), timeout=5):
            return True
    except:
        pass

    return False

CONFIG_FILE = "/etc/keepalive.conf"

with open(CONFIG_FILE, mode="rb") as fp:
    config = tomllib.load(fp)
    if not config:
        print(f"{CONFIG_FILE} not found")

DNS_SERVER = config.get("wg_dns_server", None)
if not DNS_SERVER:
    print("Property wg_dns_server not defined")
    sys.exit(1)

while True:
    dt = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if keep_alive(DNS_SERVER):
        print(f"[{dt}] Keeping Alive...")
    else:
        print(f"[{dt}] 已中断，请重启隧道")
    time.sleep(random.randint(30, 60))  # 随机在 [30 - 60] 秒内检测一次

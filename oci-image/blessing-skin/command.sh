#!/bin/bash
set -e

# 修正 /app 权限
chown -R www-data:www-data /app

# 首次启动时将源码复制到 /app，后续重启保留已有数据
if [ -z "$(ls -A /app)" ]; then
    echo "==> /app is empty, initializing source code..."
    cp --recursive --preserve=mode,ownership /src/. /app/
    echo "==> Initialization complete"
else
    echo "==> /app is not empty, skipping source copy"
fi

# 补充 Apache 的 ServerName 配置，否则会在访问时提示 "Invalid Host header" 错误
echo "ServerName localhost" >> /etc/apache2/apache2.conf

# 创建 Sqlite 数据库文件，这里必须手动创建，因为 Blessing Skin 不会自动创建数据库文件
touch /app/data.db 

exec apache2-foreground

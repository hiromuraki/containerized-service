#!/bin/bash
set -e

# 复制源码到实际的应用目录
cp --recursive --preserve=mode,ownership /src/. /app/

# 补充 Apache 的 ServerName 配置，否则会在访问时提示 "Invalid Host header" 错误
echo "ServerName localhost" >> /etc/apache2/apache2.conf

# 创建 Sqlite 数据库文件，这里必须手动创建，因为 Blessing Skin 不会自动创建数据库文件
touch /app/data.db && chown www-data:www-data /app/data.db

exec apache2-foreground
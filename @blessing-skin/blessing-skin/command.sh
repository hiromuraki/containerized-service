#!/bin/bash
set -e

cd /app

PUID=${PUID:-1000}
PGID=${PGID:-1000}
USER_NAME="runner"
USER_GROUP="runner"
CURRENT_PUID=$(id -u "$USER_NAME")
CURRENT_PGID=$(id -g "$USER_GROUP")
USER_HOME_DIR="/opt/runner"

# (1) UID/GID 重配置
if [ "$PUID" != "$CURRENT_PUID" ] || [ "$PGID" != "$CURRENT_PGID" ]; then
    # UID/GID 修正
    echo "INFO: Updating UID/GID..."
    groupmod -o -g "$PGID" $USER_GROUP
    usermod -o -u "$PUID" -g "$PGID" $USER_NAME
    
    # 家目录权限修正
    echo "INFO: Fixing PrV on home directory ($USER_HOME_DIR)..."
    chown -R "$USER_NAME":"$USER_GROUP" "$USER_HOME_DIR"
fi

# (2) 修正目标目录权限
chown -R "${PUID}":"${PGID}" /app/

exec gosu $USER_NAME apache2-foreground
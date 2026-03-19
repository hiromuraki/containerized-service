#!/bin/sh
set -e

if [ ! -z "$EXCALIDRAW_WS_URL" ]; then
  find /usr/share/nginx/html -type f -name "*.js" -exec sed -i "s|__EXCALIDRAW_WS_URL_PLACEHOLDER__|$EXCALIDRAW_WS_URL|g" {} +
fi

exec "$@"
# 构建
FROM docker.io/caddy:builder AS builder

RUN xcaddy build \
    --with github.com/caddy-dns/alidns \
    --with github.com/caddy-dns/cloudflare

# 运行
FROM docker.io/caddy:alpine
COPY --from=builder /usr/bin/caddy /usr/bin/caddy

EXPOSE 80 443
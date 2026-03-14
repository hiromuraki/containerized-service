FROM docker.io/caddy:builder AS builder

ENV GOPROXY=https://goproxy.cn,direct

RUN xcaddy build \
    --with github.com/caddy-dns/alidns \
    --with github.com/caddy-dns/cloudflare

FROM docker.io/caddy:alpine
COPY --from=builder /usr/bin/caddy /usr/bin/caddy

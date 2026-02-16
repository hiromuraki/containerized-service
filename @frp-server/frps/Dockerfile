FROM alpine:latest AS builder

RUN apk add --no-cache wget

ARG FRP_VERSION=0.67.0
ARG TARGETARCH

WORKDIR /data

RUN wget -O ./frp.tar.gz https://github.com/fatedier/frp/releases/download/v${FRP_VERSION}/frp_${FRP_VERSION}_linux_${TARGETARCH}.tar.gz \
    && tar -xf frp.tar.gz \
    && mv ./frp_${FRP_VERSION}_linux_${TARGETARCH}/frps ./


FROM alpine:latest
RUN apk add --no-cache ca-certificates tzdata

WORKDIR /app
COPY --from=builder /data/frps /usr/bin/frps

VOLUME /etc/frp

USER 1000:1000

ENTRYPOINT ["/usr/bin/frps"]
CMD ["-c", "/etc/frp/frps.toml"]
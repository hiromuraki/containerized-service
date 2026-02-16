FROM alpine:latest

RUN apk add --no-cache \
    iproute2 \
    iptables \
    wireguard-tools

COPY ./start.sh /bin/start.sh
RUN chmod +x /bin/start.sh

CMD ["start.sh"]
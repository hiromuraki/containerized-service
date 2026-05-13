FROM alpine:latest AS downloader

RUN apk add --no-cache wget unzip

RUN wget --directory-prefix=/data/skin https://github.com/bs-community/blessing-skin-server/releases/download/6.0.2/blessing-skin-server-6.0.2.zip
RUN wget --directory-prefix=/data/ https://github.com/mlocati/docker-php-extension-installer/releases/latest/download/install-php-extensions

RUN unzip /data/skin/blessing-skin-server-6.0.2.zip -d /data/skin && \
    rm /data/skin/blessing-skin-server-6.0.2.zip

FROM php:8.1-apache

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        gosu \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# 安装所需的 PHP 扩展
COPY --from=downloader /data/install-php-extensions /usr/local/bin/

RUN chmod +x /usr/local/bin/install-php-extensions && \
    install-php-extensions \
    gd \
    zip \
    pdo_sqlite

# 将服务器文件放置于 src 目录，用于复制到 /app
RUN mkdir -p /src && chown www-data:www-data /src

COPY --from=downloader --chown=www-data:www-data /data/skin /src/

RUN sed -ri -e 's!/var/www/html!${APACHE_DOCUMENT_ROOT}!g' /etc/apache2/sites-available/*.conf && \
    sed -ri -e 's!/var/www/!${APACHE_DOCUMENT_ROOT}!g' /etc/apache2/apache2.conf /etc/apache2/conf-available/*.conf && \
    a2enmod rewrite headers

COPY ./command.sh /bin/command.sh

ENV APACHE_DOCUMENT_ROOT=/app/public

VOLUME [ "/app" ]

WORKDIR /app

CMD ["bash", "/bin/command.sh"]
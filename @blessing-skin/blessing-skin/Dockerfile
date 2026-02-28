FROM alpine:latest AS builder

RUN apk add --no-cache wget unzip

RUN wget --directory-prefix=/data/skin https://github.com/bs-community/blessing-skin-server/releases/download/6.0.2/blessing-skin-server-6.0.2.zip && \
    wget --directory-prefix=/data/ https://github.com/mlocati/docker-php-extension-installer/releases/latest/download/install-php-extensions

RUN unzip /data/skin/blessing-skin-server-6.0.2.zip -d /data/skin && \
    rm /data/skin/blessing-skin-server-6.0.2.zip

FROM php:8.1-apache

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        gosu \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /data/install-php-extensions /usr/local/bin/

RUN chmod +x /usr/local/bin/install-php-extensions && \
    install-php-extensions \
    gd \
    zip \
    pdo_sqlite \
    sqlite3 \
    redis

COPY --from=builder /data/skin /app/

WORKDIR /app

ENV APACHE_DOCUMENT_ROOT /app/public
RUN sed -ri -e 's!/var/www/html!${APACHE_DOCUMENT_ROOT}!g' /etc/apache2/sites-available/*.conf && \
    sed -ri -e 's!/var/www/!${APACHE_DOCUMENT_ROOT}!g' /etc/apache2/apache2.conf /etc/apache2/conf-available/*.conf && \
    a2enmod rewrite headers

ARG DEFAULT_PUID=1000
ARG DEFAULT_PGID=1000
ARG USER_NAME=runner
ARG GROUP_NAME=runner

RUN groupadd -g ${DEFAULT_PGID} ${GROUP_NAME}
RUN useradd -u ${DEFAULT_PUID} -g ${DEFAULT_PGID} \
    -d /opt/${USER_NAME} \
    -m \
    -s /bin/bash \
    ${USER_NAME}

RUN mkdir -p /app && chown ${USER_NAME}:${GROUP_NAME} /app

COPY ./command.sh /bin/
RUN chmod +x /bin/command.sh
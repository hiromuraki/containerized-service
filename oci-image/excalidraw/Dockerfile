FROM --platform=${BUILDPLATFORM} node:24-alpine AS build

ARG NODE_ENV=production

ENV VITE_APP_WS_SERVER_URL=__EXCALIDRAW_WS_URL_PLACEHOLDER__

WORKDIR /opt/node_app

RUN apk add --no-cache git
RUN git clone --depth=1 https://github.com/excalidraw/excalidraw.git .

RUN --mount=type=cache,target=/root/.cache/yarn \
    npm_config_target_arch=${TARGETARCH} yarn --network-timeout 600000

RUN npm_config_target_arch=${TARGETARCH} yarn build:app:docker


FROM --platform=${TARGETPLATFORM} nginx:1.29-alpine

COPY --from=build /opt/node_app/excalidraw-app/build /usr/share/nginx/html
COPY ./entrypoint.sh /bin/entrypoint.sh
RUN chmod +x /bin/entrypoint.sh

HEALTHCHECK CMD wget -q -O /dev/null http://localhost || exit 1

EXPOSE 80

ENTRYPOINT [ "/bin/entrypoint.sh" ]

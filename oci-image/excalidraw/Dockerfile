FROM node:24-alpine AS build

ARG NODE_ENV=production

ENV VITE_APP_WS_SERVER_URL=https://draw-collab.daveny.top

WORKDIR /opt/node_app

RUN apk add --no-cache git
RUN git clone https://github.com/excalidraw/excalidraw.git .

RUN yarn build:app:docker

FROM nginx:1.29-alpine

COPY --from=build /opt/node_app/excalidraw-app/build /usr/share/nginx/html

HEALTHCHECK CMD wget -q -O /dev/null http://localhost || exit 1

EXPOSE 80
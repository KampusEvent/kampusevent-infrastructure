# Railway build dari repo root (build context = /).
# Docker Compose lokal tetap pakai gateway/Dockerfile dengan context ./gateway.

FROM nginx:1.25-alpine

RUN apk add --no-cache gettext wget

COPY gateway/nginx.conf.template /etc/nginx/nginx.conf.template
COPY gateway/cors.inc /etc/nginx/cors.inc
COPY gateway/docker-entrypoint.sh /docker-entrypoint.sh
RUN sed -i 's/\r$//' /docker-entrypoint.sh && chmod +x /docker-entrypoint.sh

ENTRYPOINT ["/docker-entrypoint.sh"]

FROM nginx:1.25-alpine

RUN apk add --no-cache gettext wget

COPY nginx.conf.template /etc/nginx/nginx.conf.template
COPY cors.inc /etc/nginx/cors.inc
COPY docker-entrypoint.sh /docker-entrypoint.sh
RUN sed -i 's/\r$//' /docker-entrypoint.sh && chmod +x /docker-entrypoint.sh

# Railway injects PORT — nginx listens via docker-entrypoint.sh; do not EXPOSE fixed port.
ENTRYPOINT ["/docker-entrypoint.sh"]

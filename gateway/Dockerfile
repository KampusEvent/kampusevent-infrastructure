FROM nginx:1.25-alpine

COPY nginx.conf /etc/nginx/nginx.conf
COPY cors.inc /etc/nginx/cors.inc

EXPOSE 80

HEALTHCHECK --interval=10s --timeout=3s --retries=3 \
    CMD wget -qO- http://localhost/gateway/health || exit 1

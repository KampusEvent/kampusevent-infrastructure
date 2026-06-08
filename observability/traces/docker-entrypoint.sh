#!/bin/sh
set -eu

export PORT="${PORT:-8080}"

/usr/local/bin/jaeger-all-in-one &
JAEGER_PID=$!

i=0
while [ "$i" -lt 30 ]; do
    if wget -qO- http://127.0.0.1:16686 >/dev/null 2>&1; then
        break
    fi
    i=$((i + 1))
    sleep 1
done

/otelcol-contrib --config=/etc/otelcol/config.yaml &
COLLECTOR_PID=$!

envsubst '${PORT}' < /etc/nginx/nginx.conf.template > /etc/nginx/nginx.conf
nginx -g 'daemon off;' &
NGINX_PID=$!

trap 'kill "$JAEGER_PID" "$COLLECTOR_PID" "$NGINX_PID" 2>/dev/null || true' INT TERM

wait "$NGINX_PID"

#!/bin/sh
set -eu

export PORT="${PORT:-80}"
export AUTH_SERVICE_URL="${AUTH_SERVICE_URL:-http://auth-service:8001}"
export EVENT_SERVICE_URL="${EVENT_SERVICE_URL:-http://event-service:8002}"
export REGISTRATION_SERVICE_URL="${REGISTRATION_SERVICE_URL:-http://registration-service:8003}"
export ATTENDANCE_SERVICE_URL="${ATTENDANCE_SERVICE_URL:-http://attendance-service:8004}"
export FRONTEND_ORIGIN="${FRONTEND_ORIGIN:-http://localhost:5173}"
# Long Railway hostnames break nginx map literals — use regex instead.
export FRONTEND_ORIGIN_REGEX="$(printf '%s' "$FRONTEND_ORIGIN" | sed 's/[.]/\\./g')"
export NGINX_RESOLVER="${NGINX_RESOLVER:-127.0.0.11}"

envsubst '${AUTH_SERVICE_URL} ${EVENT_SERVICE_URL} ${REGISTRATION_SERVICE_URL} ${ATTENDANCE_SERVICE_URL} ${FRONTEND_ORIGIN_REGEX} ${PORT} ${NGINX_RESOLVER}' \
  < /etc/nginx/nginx.conf.template > /etc/nginx/nginx.conf

exec nginx -g 'daemon off;'

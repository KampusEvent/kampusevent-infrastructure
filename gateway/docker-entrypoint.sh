#!/bin/sh
set -eu

ensure_url_scheme() {
  url="$1"
  case "$url" in
    http://*|https://*) printf '%s' "$url" ;;
    *) printf 'https://%s' "$url" ;;
  esac
}

normalize_origin() {
  origin="$1"
  origin="$(printf '%s' "$origin" | sed 's:/*$::')"
  ensure_url_scheme "$origin"
}

export PORT="${PORT:-80}"
export AUTH_SERVICE_URL="$(ensure_url_scheme "${AUTH_SERVICE_URL:-http://auth-service:8001}")"
export EVENT_SERVICE_URL="$(ensure_url_scheme "${EVENT_SERVICE_URL:-http://event-service:8002}")"
export REGISTRATION_SERVICE_URL="$(ensure_url_scheme "${REGISTRATION_SERVICE_URL:-http://registration-service:8003}")"
export ATTENDANCE_SERVICE_URL="$(ensure_url_scheme "${ATTENDANCE_SERVICE_URL:-http://attendance-service:8004}")"
export FRONTEND_ORIGIN="$(normalize_origin "${FRONTEND_ORIGIN:-http://localhost:5173}")"
export FRONTEND_ORIGIN_REGEX="$(printf '%s' "$FRONTEND_ORIGIN" | sed 's/[.]/\\./g')"
export NGINX_RESOLVER="${NGINX_RESOLVER:-127.0.0.11}"

envsubst '${AUTH_SERVICE_URL} ${EVENT_SERVICE_URL} ${REGISTRATION_SERVICE_URL} ${ATTENDANCE_SERVICE_URL} ${FRONTEND_ORIGIN_REGEX} ${PORT} ${NGINX_RESOLVER}' \
  < /etc/nginx/nginx.conf.template > /etc/nginx/nginx.conf

exec nginx -g 'daemon off;'

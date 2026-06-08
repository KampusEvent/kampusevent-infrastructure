#!/bin/sh
set -eu

if [ -z "${GATEWAY_URL:-}" ]; then
    echo "GATEWAY_URL is required (e.g. https://kampusevent-infrastructure-production.up.railway.app)" >&2
    exit 1
fi

GATEWAY_HOST="$(printf '%s' "$GATEWAY_URL" | sed -E 's#^https?://##' | sed 's#/.*$##')"
export GATEWAY_HOST

envsubst '${GATEWAY_HOST}' < /etc/prometheus/prometheus.yml.template > /etc/prometheus/prometheus.yml

exec /bin/prometheus \
    --config.file=/etc/prometheus/prometheus.yml \
    --storage.tsdb.path=/prometheus \
    --web.listen-address="0.0.0.0:${PORT:-9090}"

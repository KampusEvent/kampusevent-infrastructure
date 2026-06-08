#!/bin/sh
set -eu

if [ -z "${PROMETHEUS_URL:-}" ]; then
    echo "PROMETHEUS_URL is required (e.g. https://kampusevent-prometheus-production.up.railway.app)" >&2
    exit 1
fi

if [ -z "${JAEGER_URL:-}" ]; then
    echo "JAEGER_URL is required (e.g. https://kampusevent-traces-production.up.railway.app)" >&2
    exit 1
fi

mkdir -p /etc/grafana/provisioning/datasources /etc/grafana/provisioning/dashboards
sed -e "s|\${PROMETHEUS_URL}|${PROMETHEUS_URL}|g" \
    -e "s|\${JAEGER_URL}|${JAEGER_URL}|g" \
    /etc/grafana/provisioning/datasources/datasource.yml.template \
    > /etc/grafana/provisioning/datasources/datasource.yml
cp /etc/grafana/provisioning/dashboards/dashboard.yml /etc/grafana/provisioning/dashboards/dashboards.yml

export GF_SERVER_HTTP_PORT="${PORT:-3000}"
export GF_SECURITY_ADMIN_USER="${GRAFANA_ADMIN_USER:-admin}"
export GF_SECURITY_ADMIN_PASSWORD="${GRAFANA_ADMIN_PASSWORD:-admin}"
export GF_USERS_ALLOW_SIGN_UP="false"

exec /run.sh

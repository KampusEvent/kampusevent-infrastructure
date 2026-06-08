# KampusEvent — Observability (Railway)

Deploy tiga service tambahan di **project Railway Gateway** (`kampusevent-infrastructure`).

## Arsitektur

```
Backend services (Railway)
  │  OTEL HTTP POST /v1/traces
  ▼
Traces (Jaeger + OTEL Collector + nginx)
  │
  ├─► Jaeger UI  GET /
  │
Prometheus ──scrape HTTPS──► Gateway /auth/metrics, /events/metrics, ...
  │
  ▼
Grafana (RED dashboard + Jaeger datasource)
```

## Setup di Railway

Untuk tiap folder di bawah, buat **New Service** di project infrastructure → connect repo yang sama → set **Root Directory**:

| Folder | Root Directory | Variables |
|--------|----------------|-----------|
| `traces/` | `observability/traces` | — |
| `prometheus/` | `observability/prometheus` | `GATEWAY_URL` |
| `grafana/` | `observability/grafana` | `PROMETHEUS_URL`, `JAEGER_URL`, `GRAFANA_ADMIN_PASSWORD` |

Generate domain untuk masing-masing. Lalu di **Auth, Event, Registration, Attendance**:

```env
OTEL_EXPORTER_OTLP_ENDPOINT=https://<traces-domain>
```

Redeploy keempat backend.

## Verifikasi

```bash
# Metrics lewat gateway
curl https://<GATEWAY_URL>/auth/metrics

# Prometheus healthy
curl https://<PROMETHEUS_URL>/-/healthy

# Jaeger UI
open https://<TRACES_URL>/

# Grafana
open https://<GRAFANA_URL>/
```

Setelah login ke app, trace harus muncul di Jaeger (filter service: `auth-service`, dll.).

## Lokal vs Railway

| | Lokal (docker-compose) | Railway |
|--|------------------------|---------|
| Tracing | `http://jaeger:4317` (gRPC) | `https://<TRACES_URL>` (HTTP) |
| Metrics scrape | `auth-service:8001` internal | Gateway HTTPS paths |
| Grafana | `localhost:3000` | Public Grafana service |

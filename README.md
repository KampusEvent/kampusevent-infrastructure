# KampusEvent Infrastructure

Repository integrasi untuk seluruh microservices KampusEvent.

## Tanggung Jawab

- Docker Compose orchestration (semua service + database + observability)
- Konfigurasi Prometheus, Grafana, Jaeger
- End-to-End testing
- Dokumentasi integrasi

## Prerequisites

- Docker & Docker Compose
- Semua service repo ada sebagai sibling directory:
  ```
  FP AMA/
  ├── kampusevent-auth-service/
  ├── kampusevent-event-service/
  ├── kampusevent-registration-service/
  ├── kampusevent-attendance-service/
  └── kampusevent-infrastructure/   ← kamu di sini
  ```

## Quick Start

```bash
cp .env.example .env
docker compose up --build
```

## Service URLs

| Service | URL | Port |
|---------|-----|------|
| Auth | http://localhost:8001 | 8001 |
| Event | http://localhost:8002 | 8002 |
| Registration | http://localhost:8003 | 8003 |
| Attendance | http://localhost:8004 | 8004 |
| Prometheus | http://localhost:9090 | 9090 |
| Grafana | http://localhost:3000 | 3000 |
| Jaeger UI | http://localhost:16687 | 16687 |

**Grafana login:** admin / admin (default)

## End-to-End Tests

Pastikan stack sudah running, lalu:

```bash
cd e2e-tests
pip install -r requirements.txt
pytest -v
```

- `test_all_services_health` — verifikasi semua service up
- `test_full_event_flow` — skenario lengkap (skip/TODO)

## Troubleshooting

**Service tidak start:** Cek logs dengan `docker compose logs <service-name>`

**Prometheus tidak scrape:** Pastikan semua service healthy di `docker compose ps`

**Jaeger tidak menerima trace:** Verifikasi `OTEL_EXPORTER_OTLP_ENDPOINT=http://jaeger:4317` di setiap service

## Definition of Done

- [ ] Docker Compose works (all services up)
- [ ] Prometheus scrapes all /metrics
- [ ] Grafana RED dashboard visible
- [ ] Jaeger receives traces
- [ ] E2E health test passes
- [ ] E2E full flow test implemented and passes

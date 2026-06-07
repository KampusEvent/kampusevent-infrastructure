# KampusEvent Infrastructure

Repository integrasi untuk seluruh microservices KampusEvent.

## Tanggung Jawab

- Docker Compose orchestration (semua service + database + observability)
- Konfigurasi Prometheus, Grafana, Jaeger
- End-to-End & Contract testing
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

**Environment variables penting:** `JWT_SECRET`, `INTERNAL_API_KEY` (shared Registration ↔ Attendance)

## Service URLs

| Service | URL | Port |
|---------|-----|------|
| Auth | http://localhost:8001 | 8001 |
| Event | http://localhost:8002 | 8002 |
| Registration | http://localhost:8003 | 8003 |
| Attendance | http://localhost:8004 | 8004 |
| **API Gateway** | **http://localhost:8080** | **8080** |
| Prometheus | http://localhost:9090 | 9090 |
| Grafana | http://localhost:3000 | 3000 |
| Jaeger UI | http://localhost:16687 | 16687 |

**Grafana login:** admin / admin (default)

## Dokumentasi Integrasi

Lihat [INTEGRATION.md](INTEGRATION.md) untuk panduan lengkap:
- Skenario manual step-by-step
- Service communication map
- Observability guide
- Troubleshooting

## End-to-End Tests

Pastikan stack sudah running, lalu:

```bash
cd e2e-tests
pip install -r requirements.txt
pytest -v
```

| Test | Deskripsi |
|------|-----------|
| `test_e2e_flow.py` | Full flow end-to-end |
| `test_phase1_flow.py` | Auth + Event |
| `test_phase2_flow.py` | Registration |
| `test_phase3_flow.py` | Attendance |
| `test_contract_event.py` | Contract Registration ↔ Event |
| `test_contract_registration.py` | Contract Attendance ↔ Registration |
| `test_observability.py` | Prometheus targets & metrics |
| `test_gateway.py` | API Gateway routing & rate limiting |

## API Gateway

Single entry point untuk client eksternal: **http://localhost:8080**

| Gateway Path | Service |
|--------------|---------|
| `/auth/*` | Auth Service |
| `/events` | Event Service |
| `/registrations` | Registration Service |
| `/attendance` | Attendance Service |
| `/gateway/health` | Gateway health check |

Rate limiting (NGINX):
- General API: 100 req/s per IP (burst 50)
- Auth endpoints: 10 req/s per IP (burst 20)
- Login/register: 5 req/min per IP (burst 3) → HTTP 429

Lihat [INTEGRATION.md](INTEGRATION.md) untuk detail routing.

## Troubleshooting

**Service tidak start:** `docker compose logs <service-name>`

**Prometheus tidak scrape:** http://localhost:9090/targets — pastikan semua UP

**Jaeger tidak menerima trace:** Verifikasi `OTEL_EXPORTER_OTLP_ENDPOINT=http://jaeger:4317`

**Grafana kosong:** Jalankan E2E tests untuk generate traffic, lalu refresh dashboard

## Definition of Done

- [x] Docker Compose works (all services up)
- [x] Prometheus scrapes all /metrics
- [x] Grafana RED dashboard visible
- [x] Jaeger receives traces
- [x] E2E health test passes
- [x] E2E full flow test passes
- [x] Contract tests pass
- [x] API Gateway routing & rate limiting
- [x] Service-to-service auth documented

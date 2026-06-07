# KampusEvent Infrastructure

Repository integrasi untuk seluruh microservices KampusEvent.

## Tanggung Jawab

- Docker Compose orchestration (semua service + database + observability)
- API Gateway (NGINX) — single entry point `:8080`
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
  ├── kampusevent-frontend/          ← React UI (opsional, jalankan terpisah)
  └── kampusevent-infrastructure/   ← kamu di sini
  ```

## Quick Start

```bash
cp .env.example .env
docker compose up --build
```

**Environment variables penting:** `JWT_SECRET`, `INTERNAL_API_KEY` (shared Registration ↔ Attendance)

## URLs (Host)

| Service | URL | Catatan |
|---------|-----|---------|
| **API Gateway** | http://localhost:8080 | **Satu-satunya entry point API untuk client** |
| Prometheus | http://localhost:9090 | Metrics |
| Grafana | http://localhost:3000 | Dashboard RED (admin/admin) |
| Jaeger UI | http://localhost:16687 | Distributed tracing |
| Frontend (dev) | http://localhost:5173 | `npm run dev` di `kampusevent-frontend` |

> Port service `:8001–8004` **tidak di-expose** ke host. Akses internal via Docker network (`http://auth-service:8001`, dll.).

## Dokumentasi Integrasi

Lihat [INTEGRATION.md](INTEGRATION.md) untuk panduan lengkap:
- Skenario manual step-by-step
- Service communication map
- Business rules (status event, registrasi, check-in)
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
| `test_phase3_flow.py` | Attendance (check-in saat ongoing, batalkan check-in) |
| `test_contract_auth.py` | Contract Auth `GET /me` |
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
- Login/register: 60 req/min per IP (burst 15) → HTTP 429

Lihat [INTEGRATION.md](INTEGRATION.md) untuk detail routing & CORS (credentials untuk refresh cookie).

## Deploy Railway (Gateway)

Panduan lengkap: [RAILWAY.md](RAILWAY.md) — section **API Gateway**.

| Item | Nilai |
|------|-------|
| Root Directory | **`/`** (default) atau **`gateway`** — lihat `railway.toml` |
| PostgreSQL | Tidak perlu |
| Upstreams | `AUTH_SERVICE_URL`, `EVENT_SERVICE_URL`, dll. (URL publik) |
| CORS | `FRONTEND_ORIGIN` = URL publik frontend |
| DNS | `NGINX_RESOLVER=1.1.1.1` |
| Port | Nginx listen `${PORT}` — tanpa `EXPOSE` fixed |
| Health | `GET /gateway/health` |

## Troubleshooting

**Service tidak start:** `docker compose logs <service-name>`

**Prometheus tidak scrape:** http://localhost:9090/targets — pastikan semua UP

**Jaeger tidak menerima trace:** Verifikasi `OTEL_EXPORTER_OTLP_ENDPOINT=http://jaeger:4317`

**Grafana kosong:** Jalankan E2E tests untuk generate traffic, lalu refresh dashboard

**CORS / cookie:** Frontend dev pakai Vite proxy; gateway sudah set `Access-Control-Allow-Credentials`

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
- [x] Gateway-only external API access

# Deploy KampusEvent ke Railway

Panduan deploy **multi-akun Railway** — setiap service punya project Railway sendiri (GitHub CD via `railway.toml`).

## Arsitektur

```
Browser → Frontend (Railway #6)
              ↓ VITE_API_BASE_URL
         API Gateway (Railway #5)
              ↓
    ┌─────────┼─────────┬─────────────┐
    ↓         ↓         ↓             ↓
  Auth     Event   Registration   Attendance
  (#1)     (#2)       (#3)          (#4)
    ↓         ↓         ↓             ↓
 Postgres  Postgres  Postgres      Postgres
```

Karena tiap service di **project Railway berbeda**, komunikasi antar-service memakai **URL publik** (`https://xxx.up.railway.app`).

---

## Aturan deploy (wajib dibaca)

### 1. Port — jangan pakai `EXPOSE` fixed di Dockerfile

Railway menyuntikkan variable `PORT` (biasanya `8080`). Aplikasi **wajib** listen di `0.0.0.0:$PORT`.

| ❌ Salah | ✅ Benar |
|---------|---------|
| `EXPOSE 8001` di Dockerfile | Tidak ada `EXPOSE` fixed |
| uvicorn di port hardcoded saja | `--port ${PORT:-8001}` |

Jika `EXPOSE` fixed ada, Railway bisa mengarahkan traffic publik ke port yang salah → **502 Application failed to respond** (health internal lolos, URL publik gagal).

**Workaround darurat:** Settings → Networking → Port = nilai `PORT` dari log deploy (mis. `8080`).

### 2. Database — pakai URL **public**

| ❌ Jangan | ✅ Pakai |
|----------|---------|
| `postgres.railway.internal` | `DATABASE_PUBLIC_URL` dari plugin PostgreSQL |
| Host `*.railway.internal` | Host `*.proxy.rlwy.net` atau `containers-*.railway.app` |

Salin `DATABASE_PUBLIC_URL` dari tab **Connect** PostgreSQL ke variable `DATABASE_URL` di service backend (project **yang sama**).

### 3. PostgreSQL harus satu project dengan backend

Di project Auth harus ada: **Auth service** + **PostgreSQL**. Begitu juga Event, Registration, Attendance.

### 4. Path API — direct vs gateway

| Akses | Login | Health |
|-------|-------|--------|
| **Langsung** ke service | `POST /login` | `GET /health` |
| **Via Gateway** | `POST /auth/login` | `GET /gateway/health` |

### 5. OpenTelemetry (opsional)

Tracing **nonaktif** jika `OTEL_EXPORTER_OTLP_ENDPOINT` kosong (default di Railway). Docker Compose lokal tetap set `http://jaeger:4317` di `docker-compose.yml`.

---

## Sebelum mulai — generate secret bersama

```bash
openssl rand -hex 32   # JWT_SECRET — Auth, Event, Registration, Attendance
openssl rand -hex 24   # INTERNAL_API_KEY — Registration + Attendance
```

| Secret | Dipakai di |
|--------|------------|
| `JWT_SECRET` | Auth, Event, Registration, Attendance |
| `INTERNAL_API_KEY` | Registration, Attendance |

---

## Urutan deploy

| Urutan | Railway Project | Repo | URL service lain? |
|--------|-----------------|------|-------------------|
| 1 | Auth | `kampusevent-auth-service` | — |
| 2 | Event | `kampusevent-event-service` | — |
| 3 | Registration | `kampusevent-registration-service` | `EVENT_SERVICE_URL` |
| 4 | Attendance | `kampusevent-attendance-service` | `EVENT_SERVICE_URL`, `REGISTRATION_SERVICE_URL` |
| 5 | Gateway | `kampusevent-infrastructure` | 4 URL backend + `FRONTEND_ORIGIN` |
| 6 | Frontend | `kampusevent-frontend` | `VITE_API_BASE_URL` |

Setelah tiap deploy: **Settings → Networking → Generate Domain** → catat URL publik.

---

## Setup umum per project

1. **New Project** → Deploy from GitHub
2. **Root Directory** (lihat tabel)
3. Tambah **PostgreSQL** (kecuali Gateway & Frontend)
4. Set `DATABASE_URL` = salinan **`DATABASE_PUBLIC_URL`** dari Postgres
5. Set variables service (lihat section per service)
6. **Generate Domain**
7. Push `main` → auto-deploy

| Repo | Root Directory |
|------|----------------|
| `kampusevent-auth-service` | `/` |
| `kampusevent-event-service` | `/` |
| `kampusevent-registration-service` | `/` |
| `kampusevent-attendance-service` | `/` |
| `kampusevent-infrastructure` | `/` (default) **atau** `gateway` |
| `kampusevent-frontend` | `/` |

---

## 1. Auth Service

| Variable | Nilai | Wajib |
|----------|-------|-------|
| `DATABASE_URL` | `DATABASE_PUBLIC_URL` dari Postgres | ✅ |
| `JWT_SECRET` | secret bersama | ✅ |
| `JWT_ALGORITHM` | `HS256` | |
| `JWT_ACCESS_EXPIRE_MINUTES` | `15` | |
| `JWT_REFRESH_EXPIRE_DAYS` | `7` | |
| `REFRESH_COOKIE_SECURE` | `true` | ✅ |
| `REFRESH_COOKIE_SAMESITE` | `none` (lowercase, tanpa tanda kutip) | ✅ |
| `SEED_USERS` | `true` (demo) / `false` (prod) | |
| `LOG_LEVEL` | `INFO` | |
| `OTEL_EXPORTER_OTLP_ENDPOINT` | *(kosongkan)* | |

**Verifikasi:**
```bash
curl https://<auth-url>/health
curl -X POST https://<auth-url>/login \
  -H "Content-Type: application/json" \
  -d '{"email":"organizer@campus.edu","password":"organizer123"}'
```

**Log deploy sukses:** migrasi Alembic tanpa error DB, uvicorn di `$PORT`, tanpa `localhost:5432` atau `railway.internal`.

Demo accounts (`SEED_USERS=true`): `organizer@campus.edu` / `organizer123`, dll.

---

## 2. Event Service

| Variable | Nilai | Wajib |
|----------|-------|-------|
| `DATABASE_URL` | `DATABASE_PUBLIC_URL` | ✅ |
| `JWT_SECRET` | sama dengan Auth | ✅ |
| `LOG_LEVEL` | `INFO` | |

**Verifikasi:** `curl https://<event-url>/health` → `{"status":"ok"}`

---

## 3. Registration Service

| Variable | Nilai | Wajib |
|----------|-------|-------|
| `DATABASE_URL` | `DATABASE_PUBLIC_URL` | ✅ |
| `JWT_SECRET` | sama dengan Auth | ✅ |
| `EVENT_SERVICE_URL` | URL publik Event | ✅ |
| `INTERNAL_API_KEY` | secret bersama | ✅ |

**Verifikasi:** `curl https://<registration-url>/health`

---

## 4. Attendance Service

| Variable | Nilai | Wajib |
|----------|-------|-------|
| `DATABASE_URL` | `DATABASE_PUBLIC_URL` | ✅ |
| `JWT_SECRET` | sama dengan Auth | ✅ |
| `EVENT_SERVICE_URL` | URL publik Event | ✅ |
| `REGISTRATION_SERVICE_URL` | URL publik Registration | ✅ |
| `INTERNAL_API_KEY` | sama dengan Registration | ✅ |

**Verifikasi:** `curl https://<attendance-url>/health`

---

## 5. API Gateway

**Root Directory:** `/` (default — pakai `railway.toml` di root repo) **atau** `gateway`.

> Build gagal *"Railpack could not determine how to build"* → push `railway.toml` + `Dockerfile` di root infra.  
> Build gagal *`docker-entrypoint.sh: not found`* → jangan pakai `gateway/Dockerfile` dari root; pakai `Dockerfile` di root repo (sudah disediakan).

| Variable | Nilai | Wajib |
|----------|-------|-------|
| `AUTH_SERVICE_URL` | URL publik Auth | ✅ |
| `EVENT_SERVICE_URL` | URL publik Event | ✅ |
| `REGISTRATION_SERVICE_URL` | URL publik Registration | ✅ |
| `ATTENDANCE_SERVICE_URL` | URL publik Attendance | ✅ |
| `FRONTEND_ORIGIN` | URL publik Frontend | ✅ |
| `NGINX_RESOLVER` | `1.1.1.1` | ✅ |

**Verifikasi:**
```bash
curl https://<gateway-url>/gateway/health
curl -X POST https://<gateway-url>/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"organizer@campus.edu","password":"organizer123"}'
```

---

## 6. Frontend

| Variable | Build time? | Wajib |
|----------|-------------|-------|
| `VITE_API_BASE_URL` = URL Gateway | ✅ **Available at Build Time** | ✅ |

Setelah Frontend deploy → update `FRONTEND_ORIGIN` di Gateway → redeploy Gateway.

---

## Troubleshooting

| Gejala | Penyebab | Solusi |
|--------|----------|--------|
| Railpack build error (Gateway) | Tanpa `railway.toml` di root | Push `railway.toml` + `Dockerfile` di root infra |
| `docker-entrypoint.sh: not found` | Build context root, COPY salah | Pakai `Dockerfile` di root (bukan `gateway/Dockerfile`) |
| `localhost:5432` refused | `DATABASE_URL` belum diset | Set dari `DATABASE_PUBLIC_URL` |
| `railway.internal` not found | URL internal / beda project | Pakai `DATABASE_PUBLIC_URL` |
| 502 Application failed to respond | Port mismatch (`EXPOSE` vs `$PORT`) | Push Dockerfile terbaru (tanpa EXPOSE) atau set Port di Networking |
| 500 login `samesite must be...` | `REFRESH_COOKIE_SAMESITE` salah | Set `none` (lowercase, tanpa `"`) — bukan `None`, `NONE`, atau kosong |
| 401 login | User belum di-seed | `SEED_USERS=true`, redeploy Auth |
| CORS error | `FRONTEND_ORIGIN` salah | Harus persis `https://...` frontend |
| Jaeger log spam | OTEL ke localhost | Kosongkan `OTEL_EXPORTER_OTLP_ENDPOINT` |
| 503 registrasi/check-in | URL service salah | Cek `EVENT_SERVICE_URL`, dll. (URL publik) |
| Gateway 500 `invalid URL prefix` | URL upstream tanpa `https://` | Set `AUTH_SERVICE_URL=https://...` (bukan hostname saja) |
| Gateway crash `map_hash_bucket_size` | URL `FRONTEND_ORIGIN` terlalu panjang | Push gateway terbaru (regex CORS) atau pakai URL frontend lebih pendek |

---

## File konfigurasi di repo

| Repo | File Railway |
|------|----------------|
| Backend (×4) | `Dockerfile`, `railway.toml`, `app/config.py` (DB URL normalize) |
| Gateway | `railway.toml` + `Dockerfile` (root), `gateway/*` (nginx template, entrypoint) |
| Frontend | `Dockerfile`, `nginx.conf.template`, `docker-entrypoint.sh`, `railway.toml` |

Migrasi: `alembic upgrade head` otomatis saat container start.

---

## Local dev tidak berubah

`docker compose up` di `kampusevent-infrastructure` tetap pakai hostname Docker internal. Compose meng-set `OTEL_EXPORTER_OTLP_ENDPOINT=http://jaeger:4317` dan port service tetap 8001–8004 di jaringan internal.

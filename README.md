# Gratitude & Affirmations — Backend

Flask + Supabase + Clerk backend for the guided two-beat ritual app (morning affirmation, evening gratitude).

## Stack

- **Python 3.12 + Flask** (modular blueprints, app factory)
- **Supabase** (Postgres + Storage) — accessed server-side with the secret key
- **Clerk** — authentication (JWT verified via JWKS)
- **Apple StoreKit 2** — subscriptions/entitlements
- **APNs** — reminders

## Project layout

```
app/
  core/         # auth (Clerk), supabase client, time/day helpers
  domains/      # users, content, ritual, progress, billing, reminders
  workers/      # reminder scheduler
migrations/     # SQL to create the schema (run in Supabase)
seeds/          # starter free content + intro journey
```

## Setup

```bash
cd Gratitude-App-Backend
python3.12 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env   # then fill in secrets
```

## Create the Supabase tables

Run these in the **Supabase SQL Editor** in order:

1. `migrations/0001_init.sql` — tables + indexes
2. `migrations/0002_functions.sql` — `upsert_day_stat` RPC + RLS lockdown
3. `seeds/0003_seed.sql` — starter free content + intro journey

Also create two **Storage buckets** (private): `audio` and `images`.

## Run

```bash
gunicorn wsgi:app            # production
python wsgi.py               # local dev (port 8000)
curl localhost:8000/healthz  # -> {"status":"ok"}
```

## Auth

Clients authenticate with the **Clerk iOS SDK** and send `Authorization: Bearer <jwt>`. The API verifies the token against Clerk's JWKS and JIT-provisions the app user on first call.

## Key endpoints

| Method | Path | Purpose |
|--------|------|---------|
| GET | /v1/me | Profile + entitlement (provisions on first call) |
| GET | /v1/today | Time-aware beat + prompt |
| POST | /v1/completions | Record a beat (drives "days you showed up") |
| GET | /v1/progress | Lifetime day count |
| GET | /v1/journeys | Journeys (premium flagged, not hidden) |
| POST | /v1/billing/apple/verify | Verify StoreKit transaction |

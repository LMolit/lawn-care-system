# Lawn Care Business System

A self-hosted business management system for a lawn care company. It replaces spreadsheets and manual tracking with one place to manage leads, customers, jobs, routes, invoices, payments, and expenses.

The long-term setup is a public website, a mobile app for day-to-day work, and a backend API on a single server. Clients never talk to the database directly.

## What is built today

The **backend API** is the working product. It includes:

- JWT login (access and refresh tokens)
- Lead capture and converting a lead into a customer
- Customers, properties (with map coordinates), and services
- Job scheduling, start/complete, and routing for a day’s stops
- Invoices (PDF + email), payments, expenses, and basic analytics
- Automated tests and GitHub Actions CI against PostgreSQL + PostGIS

The **web app** is a Next.js starter and is not a finished product UI yet. The **mobile app** and production hosting (reverse proxy, Cloudflare Tunnel, full Docker stack) are planned and not started.

## Stack

| Layer | Choice |
|-------|--------|
| API | Python, FastAPI |
| Database | PostgreSQL + PostGIS |
| ORM / migrations | SQLAlchemy 2 + Alembic |
| Auth | JWT (no third-party login) |
| Routing | OpenRouteService + nearest-neighbor (simpler algorithms first) |
| Invoicing | HTML template → PDF → email (Resend) |
| Web (in progress) | Next.js, React, Tailwind |
| Mobile (planned) | React Native + Expo |
| Infra (planned) | Docker Compose, Caddy, Cloudflare Tunnel |

## How it is organized

```
backend/   FastAPI app, database models, migrations, tests
web/       Next.js frontend (starter)
infra/     Local Postgres/PostGIS for development
mobile/    Planned field app (empty)
packages/  Planned shared API client (empty)
```

## Design notes (short)

- Public-facing records (leads, reviews) use UUIDs so IDs are harder to guess. Internal tables use simple integer IDs.
- One-person company for now, so there is a single admin role. Crew accounts, recurring jobs, and a job queue are deferred until they are needed.
- Everything goes through the API so the website and a future mobile app can share the same business logic.

## Status

Actively in development. Backend and database are the mature parts of the repo. Frontend and mobile are next.

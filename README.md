# Lawn Care Business System

A self hosted, full stack business management system for my lawn care business.

## What it does

Replaces manual lead tracking, scheduling, routing, job tracking, invoicing, with one system. Public lead-capture site, a backend API with the actual business logic, and a mobile app for day to day use.

## Architecture

Internet
|
|
Cloudflare Tunnel -> reverse proxy
|
|-> FastAPI backend —--> PostgreSQL + PostGIS
|      |
|      |-> Next.js(public site) 
|
|-> Mobile app

Both the public site and Mobile app talk to the backend not directly to the database. 

Single VM, for docker compose services (proxy, web, backend, database). No client ever talks to the database directly, everything goes through the backend API.

## Stack

|Layer | Choice |
|------|--------|
|Database| PostgreSQL + PostGis|
|ORM/migrations | SQLAlchemy 2.x + Alembic |
|Backend | Python, FastAPI |
|Routing algorithm | Custom nearest neighbor (phase 1) 2-opt / simulated annealing (planned for phase 2) |
|Web | Next.js, Tailwind |
|Mobile | React Native + Expo, offline built work queue |
|Auth | JWT no third party provider |

|Infra | docker compose, caddy, cloudflare tunnel |

## engineering decisions

- Circular foreign key between leads and customers (each references the other), deferred one constraint to a second migration once both tables exist.
- UUID vs integer primary keys chosen per table. UUIDs only used on tables reachable via public endpoints(leads, reviews). This is to prevent ID enumeration, sequential ints everywhere else for simplicity when there is no exposure risk.

## deferred to phase 2

|feature | why deferred |
|--------|--------------|
|Background task queue | Not enough volume to be worth it currently |
|Recurring job auto generation | manual creation fine for now |
|Role based access/multi user | Only one person running the company with no employees, will add it if needed |
|ios build | owner uses android so not needed and to save on apple developer pack no apple app |
| automated backups | This is not necessary until we have data to back up, and as a small system won't be essential at first |

## status

Actively in development. Currently built, database schema (users, leads, customers, circular FK resolved and verified).


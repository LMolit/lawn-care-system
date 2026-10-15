# Admin App System Overview

This document describes the part of the system that is already built and relevant for a non-technical admin dashboard or operations portal. It is intentionally informational rather than a build specification.

## Purpose

The admin app is intended to give a business owner or office admin visibility into the operating system and the business itself. The current backend supports the following kinds of admin work:

- review and manage leads
- view and update customer and property records
- manage service catalog and scheduling
- monitor jobs and routes
- review approved customer feedback
- create and send invoices and record payments
- log expenses and review profitability
- review monthly business performance metrics

The repo currently contains a FastAPI backend, a partial Next.js website, and planned mobile/admin interfaces. The built system that an admin app can consume is the backend API.

## Current system status

What is already in place:

- FastAPI backend with JWT auth
- PostgreSQL + PostGIS database
- SQLAlchemy models and Alembic migrations
- lead capture, customer conversion, job scheduling, invoicing, and expense tracking
- analytics endpoints for revenue, profitability, and performance summaries

What is not fully built yet:

- a finished admin UI
- a complete website analytics dashboard for traffic and user behavior
- a dedicated mobile admin app
- route optimization beyond a simple nearest-neighbor approach

## Core architecture

The system is organized around a central API. The website and future admin/mobile apps should consume the same backend instead of talking directly to the database.

Primary architecture pieces:

- API layer: FastAPI at `backend/app`
- Database layer: PostgreSQL + PostGIS via SQLAlchemy
- Auth: JWT-based access tokens and refresh tokens
- Business logic: CRUD and service modules under `backend/app/crud`
- External integrations: invoice PDF/email, route generation, and planned future hosting/proxy services

## Authentication and access

The system currently uses a single admin-style internal user model.

Authentication endpoints:

- `POST /api/v1/auth/login`
- `POST /api/v1/auth/refresh`
- `GET /api/v1/auth/me`

Authentication model:

- login returns access and refresh JWT tokens
- refresh endpoint exchanges a valid refresh token for a new access token
- most business endpoints require a valid authenticated user

Current user model includes:

- email
- password hash
- name
- phone
- active status

## Health and operational endpoints

- `GET /health` — confirms the API and database are online

This is useful for admin monitoring or uptime checks.

## Admin-relevant API surface

### Leads

Leads are public intake records created from website forms or sales inquiries.

Endpoints:

- `POST /api/v1/leads` — create a lead
- `POST /api/v1/leads/{lead_id}/convert` — convert a lead into a customer
- `GET /api/v1/leads` — list leads with filters and pagination

Lead fields:

- UUID id
- name
- email
- phone
- address
- message
- status: `new`, `contacted`, `quoted`, `converted`, `lost`
- converted customer id
- timestamps

Admin value:

- this is the funnel for incoming sales leads
- admin dashboards can track lead volume, conversion rate, and status progression

### Reviews

Reviews are user-submitted testimonials and they can be approved before publishing.

Endpoints:

- `POST /api/v1/reviews` — submit a review
- `GET /api/v1/reviews` — list approved public reviews
- `PATCH /api/v1/reviews/{review_id}/approve` — approve or unapprove a review

Review fields:

- UUID id
- customer_id (optional)
- name
- rating (1-5)
- comment
- approved flag

Admin value:

- admin app can review new review submissions
- approval flow matches the requirement to moderate and publish reviews

### Customers

Customers represent active or historical business clients.

Endpoints:

- `POST /api/v1/customers` — create a customer
- `PATCH /api/v1/customers/{id}` — update a customer
- `GET /api/v1/customers` — list customers with optional active filter and pagination

Customer fields:

- id
- name
- email
- phone
- notes
- lead_id (optional)
- active
- timestamps

Admin value:

- customer list is the central account directory
- this is a key source for billing, property lookup, and work history

### Properties

Properties are individual job locations attached to a customer.

Endpoints:

- `POST /api/v1/properties` — create a property
- `GET /api/v1/properties` — list properties
- `GET /api/v1/properties/{id}` — get one property
- `PATCH /api/v1/properties/{id}` — update a property

Property fields:

- id
- customer_id
- address
- location (PostGIS POINT in WGS84 / lat-long)
- lawn_size_sqft
- access_notes

Admin value:

- needed for route planning and customer site management
- gives the admin app address, location, and property access information

### Services

Service catalog records the work offerings and pricing model.

Endpoints:

- `POST /api/v1/services` — create a service
- `PATCH /api/v1/services/{id}` — update a service
- `GET /api/v1/services` — list services

Service fields:

- id
- name
- description
- base_price
- estimated_duration_minutes

Admin value:

- supports pricing and scheduling configuration
- service catalog is referenced by jobs

### Jobs

Jobs are scheduled work items for a customer at a property.

Endpoints:

- `POST /api/v1/jobs` — create a job
- `GET /api/v1/jobs` — list jobs with optional status and customer filters
- `GET /api/v1/jobs/{id}` — get a job
- `PATCH /api/v1/jobs/{id}` — update a job
- `POST /api/v1/jobs/{id}/start` — mark a job as in progress with GPS location and timestamp
- `POST /api/v1/jobs/{id}/complete` — mark a job complete with GPS location and timestamp

Job fields:

- id
- customer_id
- property_id
- service_id
- scheduled_date
- status: `scheduled`, `in_progress`, `completed`, `cancelled`
- estimated_duration_minutes
- actual_duration_minutes
- price
- job_type: `routine`, `seasonal`
- notes
- timestamps

Important operational behavior:

- starting a job writes a job event with a location and timestamp
- completing a job writes a completion event and estimates actual duration from the start time

Admin value:

- this is the core day-to-day operational record
- it supports scheduling, status tracking, duration analysis, and route assignment

### Routes

Routes are generated daily for job sequencing.

Endpoints:

- `POST /api/v1/routes/generate` — generate a route for a date
- `GET /api/v1/routes/today` — fetch today’s route

Route fields:

- id
- date
- status: `planned`, `in_progress`, `completed`
- total_distance_miles
- total_duration_minutes
- algorithm_used
- stops list

Route stop fields:

- id
- route_id
- job_id
- sequence_order
- estimated_arrival_time
- actual_arrival_time

Current route logic:

- planned jobs for a date are selected
- a simple nearest-neighbor algorithm is used to order stops
- home base is currently a hard-coded constant rather than a stored business location value

Admin value:

- route data is directly relevant to field operations and daily scheduling

### Invoices

Invoices are generated for customer billing.

Endpoints:

- `POST /api/v1/invoices` — create an invoice
- `POST /api/v1/invoices/{id}/send` — send invoice
- `GET /api/v1/invoices/{id}` — get invoice

Invoice fields:

- id
- customer_id
- invoice_number
- issue_date
- due_date
- status: `draft`, `sent`, `paid`, `overdue`, `void`
- subtotal
- tax
- total
- sent_at
- line items

Related invoice data:

- invoice counter table for sequential numbering
- invoice line items with job references

Admin value:

- this is essential for receivables, payment follow-up, and financial reporting

### Payments

Payments record invoices being paid.

Endpoints:

- `POST /api/v1/payments` — record a payment

Payment fields:

- id
- invoice_id
- amount
- method: `cash`, `check`, `card`, `online`, `zelle`, `venmo`
- paid_at
- transaction_ref

Admin value:

- supports payment tracking and reconciliation

### Expenses

Expenses support operational cost tracking.

Endpoints:

- `POST /api/v1/expenses` — create an expense
- `GET /api/v1/expenses` — list expenses
- `GET /api/v1/expenses/{id}` — get one expense
- `PATCH /api/v1/expenses/{id}` — update an expense

Expense fields:

- id
- category_id
- description
- amount
- date
- vendor
- job_id (optional)

Expense categories:

- id
- name

Admin value:

- allows cost tracking by category and job
- necessary for profit/loss analysis

### Analytics

Analytics endpoints provide business-level dashboards for an admin user.

Endpoints:

- `GET /api/v1/analytics/overview`
- `GET /api/v1/analytics/profit-loss?start_date=YYYY-MM-DD&end_date=YYYY-MM-DD`

Overview metrics currently include:

- revenue this month
- jobs completed this month
- active customers
- average job duration

Profit/loss data currently includes:

- revenue
- expenses
- profit
- expenses grouped by category

Admin value:

- this is the closest thing to a reporting dashboard already available in the system
- it covers financial and operations summaries, even though the UI is not complete yet

## Database model summary

The database is the core source of truth. Core tables include:

### User and auth

- `users`
  - id
  - email
  - password_hash
  - name
  - phone
  - active
  - timestamps

### Sales funnel

- `leads`
  - id (UUID)
  - name
  - email
  - phone
  - address
  - message
  - status
  - converted_customer_id
  - timestamps

### Customers and properties

- `customers`
  - id
  - name
  - email
  - phone
  - notes
  - lead_id
  - active
  - timestamps

- `properties`
  - id
  - customer_id
  - address
  - location (POINT geography)
  - lawn_size_sqft
  - access_notes
  - timestamps

### Service catalog

- `services`
  - id
  - name
  - description
  - base_price
  - estimated_duration_minutes
  - timestamps

### Jobs and field activity

- `jobs`
  - id
  - customer_id
  - property_id
  - service_id
  - scheduled_date
  - status
  - estimated_duration_minutes
  - actual_duration_minutes
  - price
  - job_type
  - notes
  - timestamps

- `job_events`
  - id
  - job_id
  - event_type (`started`, `completed`)
  - timestamp
  - location (POINT geography)
  - timestamps

### Routing

- `routes`
  - id
  - date
  - status
  - total_distance_miles
  - total_duration_minutes
  - algorithm_used
  - timestamps

- `route_stops`
  - id
  - route_id
  - job_id
  - sequence_order
  - estimated_arrival_time
  - actual_arrival_time
  - timestamps

### Billing and finance

- `invoices`
  - id
  - customer_id
  - invoice_number
  - issue_date
  - due_date
  - status
  - subtotal
  - tax
  - total
  - sent_at
  - timestamps

- `invoice_line_items`
  - id
  - invoice_id
  - job_id
  - description
  - quantity
  - unit_price
  - total
  - timestamps

- `invoice_counter`
  - id
  - count

- `payments`
  - id
  - invoice_id
  - amount
  - method
  - paid_at
  - transaction_ref
  - timestamps

### Expenses

- `expense_categories`
  - id
  - name
  - timestamps

- `expenses`
  - id
  - category_id
  - description
  - amount
  - date
  - vendor
  - job_id
  - timestamps

### Reviews

- `reviews`
  - id (UUID)
  - customer_id (optional)
  - name
  - rating
  - comment
  - approved
  - timestamps

## Important data relationships

The business model is heavily interconnected:

- a customer may have many properties
- a property belongs to one customer
- a job belongs to one customer and one property
- a job uses one service
- a route contains many stops, each tied to a job
- an invoice belongs to a customer and may include multiple jobs through line items
- a payment belongs to an invoice
- an expense may be linked to a job and a category
- a lead can convert into a customer
- a customer may have a review

## Admin app opportunities based on current system

The current backend already supports the following admin dashboard views:

- lead pipeline overview
- customer directory
- property/site directory
- job schedule and status tracker
- route view for daily work planning
- invoice and payment tracking
- expense tracking by category
- monthly revenue and profit summary
- customer review moderation

This is enough to power a useful internal operations dashboard even without a full custom admin UI yet.

## Important caveat

The repository does not yet contain an actual website traffic analytics layer. There is a public web app, and the backend includes business metrics, but there is no mature implementation of analytics for traffic, pageviews, bounce rate, conversion attribution, or external marketing data. If the admin app is expected to show website traffic, that feature would need to be added on top of the current system rather than assuming it already exists.

## Summary

The system already has the data and API foundation needed for a serious admin tool:

- operations tracking
- customer and property management
- scheduling and route management
- job status monitoring
- financial reporting
- review moderation
- service catalog and business metrics

The admin app should be built around these backend capabilities and should treat the API as the primary source of truth.

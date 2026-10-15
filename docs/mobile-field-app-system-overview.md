# Mobile Field App System Overview

This document describes the part of the system that is already built and relevant for a non-technical field app used outdoors by workers. It is informational rather than a build specification.

## Purpose

The mobile app is intended for a crew or solo technician working on-site. The field app will need to:

- pull the day’s route and job list
- navigate to each property in sequence
- mark a job as started when arriving on site
- mark a job as complete when work is done
- capture timestamps and GPS location
- view customer/property details needed to perform the work
- show job timing information for later reporting

The backend already contains the logic to support these behaviors, even though the mobile app itself is not yet built.

## Current system status

The repository already includes the backend foundation for the field workflow:

- jobs with scheduled dates and statuses
- property locations with lat/long coordinates
- route generation for a day
- GPS-based job start/complete tracking
- job duration calculation from start to finish
- admin-managed job records and customer data

The mobile app itself is still planned and is not implemented yet.

## Core backend capability for the field app

The system is designed so the field app will consume the same API used by the internal business system.

Primary relevant backend modules:

- `backend/app/routers/jobs.py`
- `backend/app/routers/routes.py`
- `backend/app/routers/properties.py`
- `backend/app/routers/customers.py`
- `backend/app/routers/auth.py`

These endpoints already provide the data model needed to support field tasks.

## Authentication

The field app must authenticate as an internal user before viewing or updating job and route data.

Authentication endpoints:

- `POST /api/v1/auth/login`
- `POST /api/v1/auth/refresh`
- `GET /api/v1/auth/me`

The field app will use the same JWT pattern as the admin app.

## Job workflow the field app needs

The current system is built around a clear field lifecycle:

1. job is created and assigned to a customer/property
2. job is scheduled for a date
3. route is generated for the day
4. worker starts the job when they arrive
5. worker completes the job when the work is done
6. actual duration is calculated and recorded

### Job status model

Jobs can be in the following states:

- `scheduled`
- `in_progress`
- `completed`
- `cancelled`

### Relevant job endpoints

- `POST /api/v1/jobs` — create a job
- `GET /api/v1/jobs` — list jobs for a user or customer
- `GET /api/v1/jobs/{id}` — fetch a specific job
- `PATCH /api/v1/jobs/{id}` — update job details
- `POST /api/v1/jobs/{id}/start` — begin work at a job
- `POST /api/v1/jobs/{id}/complete` — finish work at a job

### Job start/complete behavior

When a worker starts a job, the backend expects GPS coordinates and a timestamp.

The system stores this as a `job_event` record with:

- job_id
- event_type (`started` or `completed`)
- timestamp
- location (PostGIS POINT geography)

When a job is completed, the backend compares the completion time to the last start event and stores the difference in:

- `actual_duration_minutes`

This is the key timing data the mobile app should display after completion.

## Route workflow for field operations

Routes are central to the field app experience.

Relevant endpoints:

- `POST /api/v1/routes/generate` — generate a route for a given date
- `GET /api/v1/routes/today` — get today’s route

A route includes:

- date
- status
- total distance
- total duration
- algorithm used
- ordered stops

A route stop includes:

- route_id
- job_id
- sequence_order
- estimated arrival time
- actual arrival time

Current route generation behavior:

- selects scheduled jobs for the date
- uses a simple nearest-neighbor approach to order the stops
- starts from a business home location constant, currently defined in code

This means the field app can use the route list as a daily work sequence and drive in order rather than ad hoc.

## Property and customer data needed in the field

The app will need the job location and customer context to work correctly.

### Properties

Relevant endpoints:

- `GET /api/v1/properties`
- `GET /api/v1/properties/{id}`

Property data includes:

- address
- geolocation as a geographic POINT
- lawn size
- access notes

This is essential for navigation and on-site execution.

### Customers

Relevant endpoints:

- `GET /api/v1/customers`
- `PATCH /api/v1/customers/{id}`

Customer data includes:

- name
- contact information
- notes
- active status
- optional lead origin

This supports check-in, communication, and job context.

## Data model relevant to the field app

### Jobs

The `jobs` table is the main work record for the field app.

Key fields:

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

### Job events

The `job_events` table is what makes work tracking possible.

Fields include:

- job_id
- event_type
- timestamp
- location

This table is the basis for:

- arrival tracking
- completion tracking
- route verification
- duration reporting

### Properties with geography

The `properties` table stores each site as a location with PostGIS geography coordinates.

This supports:

- map rendering
- route planning
- geofenced job start/complete events
- turn-by-turn navigation support from a mapping provider

### Routes and stops

The `routes` and `route_stops` tables contain the daily sequence and timing expectations.

The mobile app can use:

- `sequence_order` for the next stop
- `estimated_arrival_time` for time planning
- `actual_arrival_time` for completion tracking

## How the field app should use the system today

The current app flow should be thought of as:

- user logs in
- app fetches the day’s route
- app loads each job in route order
- app loads property and customer details for each stop
- app records start and completion events with GPS and timestamps
- app displays actual time worked and completion status

This matches the system’s actual backend behavior.

## Related data that helps field work

### Services

The `services` table defines the work types and expected duration.

Useful for:

- job expectations
- estimating duration
- showing the task to the worker

### Reviews

Reviews are not field-critical, but they are part of the business system and could be displayed in an admin-only context rather than in the mobile app.

### Invoices

Invoices are relevant to office operations, not the field app itself. They are not necessary for the primary crew workflow.

## Operational constraints and realities in the current code

A few important things to know for a field app design:

- The route logic is simple and not yet a full optimization engine.
- The app uses a hard-coded home/base location for route generation.
- The field app is expected to send GPS coordinates manually for start/complete events.
- There is no separate field crew permission model yet; the current auth model is still internal-admin-oriented.
- There is no true live tracking or push notifications system in place yet.

## What the field app can already support

Based on the current backend, the mobile app can support:

- daily route view
- sequential job navigation
- job start/end recording
- GPS-based job timestamps
- actual duration capture
- property and customer lookup
- job status updates from the field

This is the strongest fit for the field worker use case in the current codebase.

## Summary

The mobile app is expected to be a route-and-job execution tool, not a general business dashboard. The backend already contains the core data needed to support that:

- scheduled jobs
- routes and stop order
- property locations
- job status tracking
- job start and completion timestamps
- actual duration recording
- customer and site context

The field app should be built around these existing capabilities, with the API as the system of record.

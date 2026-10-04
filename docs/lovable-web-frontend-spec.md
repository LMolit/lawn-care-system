# Liberty Lawn Care — Website frontend spec (for Lovable)

Build a **Vite + React + TypeScript + Tailwind** site. Connect it to an existing FastAPI backend. Do **not** invent a database, Supabase, or mock-only API as the final design. Do **not** use shadcn/ui, MUI, or a purple/SaaS dashboard template.

This is a real local lawn company site plus a private owner desk. It should look like a careful trade business, not like a generated startup landing page.

---

## Who you are building for

**Liberty Lawn Care** — Batavia, Illinois. Owner-operated. Residential lawns in and around Batavia.

Public visitors request quotes and leave reviews. The owner logs in to run the business (leads, jobs, routes, invoices, analytics).

Phone and email are **placeholders**. Put them in **one config file** (`src/config/site.ts`) so they are easy to change later. Do not scatter them.

```ts
export const site = {
  name: "Liberty Lawn Care",
  city: "Batavia, Illinois",
  serviceArea: "Batavia and nearby Kane County neighborhoods",
  phone: "(630) 000-0000", // placeholder — owner will replace
  email: "hello@libertylawncare.com", // placeholder — owner will replace
  apiBaseUrl: import.meta.env.VITE_API_URL as string,
};
```

---

## Copy (draft — keep this wording unless it is grammatically broken)

**Nav:** Liberty Lawn Care · Services · Reviews · Request a quote · Owner (small, unobtrusive, not a marketing CTA)

**Hero eyebrow:** Batavia, Illinois

**Hero headline:** Steady lawn care for Batavia yards.

**Hero subhead:** Mowing, cleanup, and seasonal work done on a schedule you can count on. No gimmicks. No five-year contracts.

**Primary button:** Request a quote  
**Secondary:** See services

**About:**
Liberty Lawn Care is a small, owner-run operation based in Batavia. The work is straightforward: keep lawns cut, edges clean, and beds in order through the season, then handle the heavier spring and fall jobs when they come due.

You deal with the same person who does the work. Quotes are based on the property, not a phone script. If a week runs wet or a mow needs to move, you hear about it.

**Services (home page — static copy; do not load these from the API):**

| Title | One line |
|---|---|
| Mowing | Regular cuts at a height that keeps the lawn thick, not scalped. |
| Bush trimming | Shape and keep shrubs from eating the sidewalk and the house. |
| Spring / fall cleanup | Leaf, debris, and bed cleanup when the season turns. |
| Mulch installation | Fresh beds, clean edges, mulch that stays put. |
| Aeration | Core aeration so water and air get to the roots. |
| Weeding | Beds and borders kept under control, not a one-time blast. |

**Quote page intro:** Tell us the address and how to reach you. A short note about the yard helps. You will get a reply from the owner, not a call center.

**Success after quote:** Thanks. We have the request and will follow up.

**Review page intro:** If we have done work at your place, leave a rating. Reviews show on the site after they are approved.

**Footer:** Liberty Lawn Care · Batavia, Illinois · phone · email · not affiliated with any national chain.

**Login page:** Owner sign in. No “Welcome back, let’s crush it.” Just email, password, Sign in.

---

## Look and feel (non-negotiable)

This must **not** look like default AI output. Avoid: Inter/Roboto as the only font, purple or electric lime, mesh gradients, glass cards, 3D grass icons, blob shapes, “your journey,” “we care about excellence,” giant rounded pills, emoji, stock photos of smiling people with clipboards, neon charts on the public site.

**Direction:** A local contractor with a printed invoice and a clean truck. Paper, soil, hedge. Quiet confidence.

**Color**

- Ink: `#1C1917`
- Paper: `#F3EEE4`
- Deep green: `#1E3F2F`
- Mid green: `#2F5D46`
- Soil brown: `#6B4F3A`
- Dry straw: `#C4B49A`
- Line: `#D9D1C3`
- Danger: `#8F2D2D`
- White: `#FFFcf7` for owner tables only if paper feels too warm

Use green for primary actions and headings. Use brown for rules, labels, and secondary buttons. Background is paper, not pure white, on the public site.

**Type**

- Headlines: `"Fraunces", "Iowan Old Style", Georgia, serif` — slightly tight tracking, not ultra-light.
- Body / UI: `"Source Sans 3", "Source Sans Pro", system-ui, sans-serif`
- Numbers in the owner desk: tabular lining if easy (`font-variant-numeric: tabular-nums`)

**Layout**

- Max content width ~1120px. Generous vertical space. Hairline borders, not drop shadows.
- Header: wordmark in serif, small caps city line under it optional.
- Hero: two columns on desktop (copy left, a **full-bleed photograph of a real mown lawn / hedge / autumn yard** right — Unsplash/Pexels is fine if it looks Midwestern residential, overcast or late-day, not tropical).
- Services: simple six-up list with a brown left border, not icon grids.
- Reviews: name, stars, quote. No avatar circles.

**Owner desk** can be denser: left nav, tables, filters. Still the same fonts and greens. No SaaS purple sidebar.

**Motion:** almost none. Hover darkens a button. No page-load animations.

---

## Pages

### Public (no auth)

| Route | What it is |
|---|---|
| `/` | Home: hero, about, services, approved reviews, quote CTA |
| `/quote` | Lead form |
| `/reviews/new` | Review form |
| `/login` | Owner login |

Shared public header + footer on those four.

### Owner (auth required)

| Route | What it is |
|---|---|
| `/app` | Redirect to `/app/jobs` or a small overview using analytics |
| `/app/leads` | List leads, filter by status, convert |
| `/app/reviews` | List is **approved-only from the public GET**. For moderation: the public GET cannot show pending reviews. Build approve by **review id** if you only have GET approved — see API notes. Prefer: show approved list + a “pending” workflow if the API cannot list unapproved (it cannot). Practical approach: after someone submits a review, owner will not see it on GET until approved. Document this in the UI: “New reviews do not appear here until you approve them by id” is a bad UX. **Workaround:** keep a local “recently submitted ids” is wrong. **Correct product for this backend:** owner moderation page that explains reviews are hidden until approved, and provide an **Approve** action that calls `PATCH` with a UUID the owner pastes **only if** we cannot list pending. Better: on the reviews page, show approved reviews with an Unapprove toggle (`approved: false`). New submissions must be approved somehow — **use GET /reviews for approved, and convert/approve from a queue is impossible without a pending list.** |

**Honest constraint:** `GET /api/v1/reviews` returns **approved reviews only**. There is **no list-pending endpoint**. For owner moderation:

- Show approved reviews with **Unapprove** (`PATCH /api/v1/reviews/{id}/approve` body `{"approved": false}`).
- Add a small “Approve by ID” field (UUID from email/notes) for first-time approval until a pending-list endpoint exists. Label it clearly as temporary.

| `/app/jobs` | List/filter jobs, create, edit, start, complete |
| `/app/routes` | Generate route for a date, show today’s route |
| `/app/invoices` | Create invoice, fetch by id, send |
| `/app/analytics` | Overview + profit/loss date range |

Owner shell: top bar with business name + Sign out. Side nav: Leads, Reviews, Jobs, Routes, Invoices, Analytics.

**Do not build** full customer/property/service admin pages. **Do** fetch those lists for dropdowns when creating jobs and invoices.

---

## Backend connection

Base URL: `import.meta.env.VITE_API_URL` with **no trailing slash**. Example local: `http://localhost:8000`

Lovable preview **cannot** call `localhost`. Set `VITE_API_URL` to a **public** FastAPI URL (Cloudflare Tunnel or ngrok to the owner’s machine, or a deployed API).

**CORS (owner must fix on the backend if calls fail):** the API currently allows only `http://localhost:3000`. Lovable + Vite will need the preview origin (and `http://localhost:5173`) added. If requests fail with a CORS error, say so in the UI instead of hanging.

**Auth is JSON JWT, not cookies.**

1. `POST /api/v1/auth/login`  
   Body: `{"email": "...", "password": "..."}`  
   Response: `{"access_token": "...", "refresh_token": "...", "token_type": "bearer"}`
2. Store both tokens in `localStorage` (keys `llc_access`, `llc_refresh`).
3. All owner requests: header `Authorization: Bearer <access_token>`.
4. On **401**, try `POST /api/v1/auth/refresh` with `{"refresh_token": "..."}`. Response is `{ access_token, token_type }`. Retry the original request once. If refresh fails, clear tokens and send to `/login`.
5. Optional: `GET /api/v1/auth/me` after login to confirm.

Public endpoints send **no** Authorization header.

**JSON errors from this API** (not always FastAPI default):

```json
{ "error": "not_found" | "conflict" | "validation_error", "message": "...", "detail": null }
```

Login failures may be `{ "detail": "Incorrect email or password" }` with status 401.

Show `message` or `detail` to the user. Never dump raw JSON on the public site.

**Pagination** on lists: `page` (default 1), `page_size` (default 25). Response shape: `{ items, total, page, page_size }`.

---

## API map (use these paths exactly)

Prefix every path with `VITE_API_URL`.

### Public

| Method | Path | Body | Notes |
|---|---|---|---|
| POST | `/api/v1/leads` | `{ name, email?, phone?, address, message? }` | `name` and `address` required. 201 |
| GET | `/api/v1/reviews?page=1&page_size=25` | — | Approved only |
| POST | `/api/v1/reviews` | `{ name, rating, comment? }` | `rating` integer 1–5. 201. Will **not** show on home until owner approves |

Lead form validation (frontend, stricter than API): name, address, **at least one of email or phone**.

### Auth

| Method | Path | Body |
|---|---|---|
| POST | `/api/v1/auth/login` | `{ email, password }` |
| POST | `/api/v1/auth/refresh` | `{ refresh_token }` |
| GET | `/api/v1/auth/me` | Bearer |

### Owner — leads

| Method | Path | Notes |
|---|---|---|
| GET | `/api/v1/leads?status=&page=&page_size=` | `status` one of `new`, `contacted`, `quoted`, `converted`, `lost` |
| POST | `/api/v1/leads/{lead_id}/convert` | `lead_id` is a **UUID**. 201 customer |

Lead object includes: `id` (UUID), `name`, `email`, `phone`, `address`, `message`, `status`, `converted_customer_id`, timestamps.

### Owner — reviews

| Method | Path | Body |
|---|---|---|
| PATCH | `/api/v1/reviews/{review_id}/approve` | `{ "approved": true \| false }` | `review_id` UUID |

Review object: `id` UUID, `customer_id`, `name`, `rating`, `comment`, `approved`, timestamps.

### Owner — lookups (dropdowns)

| Method | Path |
|---|---|
| GET | `/api/v1/customers?active=true&page=1&page_size=100` |
| GET | `/api/v1/properties?customer_id=&page=1&page_size=100` |
| GET | `/api/v1/services?page=1&page_size=100` |

Customer: `id`, `name`, `email`, `phone`, `active`, …  
Property: `id`, `customer_id`, `address`, `latitude`, `longitude`, …  
Service: `id`, `name`, `description`, `base_price`, `estimated_duration_minutes`

Filter properties by selected customer when creating a job.

### Owner — jobs

`job_type`: `routine` \| `seasonal`  
`status`: `scheduled` \| `in_progress` \| `completed` \| `cancelled`

| Method | Path | Body |
|---|---|---|
| GET | `/api/v1/jobs?status=&customer_id=&page=&page_size=` | |
| GET | `/api/v1/jobs/{id}` | |
| POST | `/api/v1/jobs` | `{ customer_id, property_id, service_id, scheduled_date (YYYY-MM-DD), job_type?, price, estimated_duration_minutes?, notes? }` | Date cannot be in the past. 201 |
| PATCH | `/api/v1/jobs/{id}` | any subset of create fields plus `status` |
| POST | `/api/v1/jobs/{id}/start` | `{ latitude, longitude, timestamp }` ISO datetime |
| POST | `/api/v1/jobs/{id}/complete` | same |

For start/complete: use `navigator.geolocation` if the owner allows it; otherwise show lat/lng fields (decimals). `timestamp` = `new Date().toISOString()`.

Start/complete only from sensible statuses; if the API returns 409/400, show `message`.

### Owner — routes

| Method | Path | Body |
|---|---|---|
| POST | `/api/v1/routes/generate` | `{ "date": "YYYY-MM-DD" }` | 201 |
| GET | `/api/v1/routes/today` | 404 if none: `{ error: "not_found", message: "No route generated for today" }` |

Response: `id`, `date`, `status`, `total_distance_miles`, `total_duration_minutes`, `algorithm_used`, `stops[]` with `job_id`, `sequence_order`, `estimated_arrival_time`, `actual_arrival_time`.

Show stops in `sequence_order`. Resolve job addresses via job + property fetches if needed (job has `property_id`).

### Owner — invoices

**There is no list-invoices endpoint.** UI:

1. Form: `customer_id`, multi-select **completed** jobs for that customer, `due_date`.
2. `POST /api/v1/invoices` `{ customer_id, job_ids: number[], due_date }` → show the created invoice (number, totals, line items).
3. Store last ids in session so the owner can reopen. Optional: “Open invoice” input for numeric `id`.
4. `GET /api/v1/invoices/{id}`
5. `POST /api/v1/invoices/{id}/send` — emails PDF; needs customer email on file.

Jobs must be `completed`, belong to that customer, and not already billed (409 conflict if billed).

Invoice: `invoice_number`, `issue_date`, `due_date`, `status` (`draft` \| `sent` \| `paid` \| `overdue` \| `void`), `subtotal`, `tax`, `total`, `sent_at`, `line_items[]`.

### Owner — analytics

| Method | Path |
|---|---|
| GET | `/api/v1/analytics/overview` |
| GET | `/api/v1/analytics/profit-loss?start_date=YYYY-MM-DD&end_date=YYYY-MM-DD` |

Overview: `revenue_this_month`, `jobs_completed_this_month`, `active_customers`, `avg_job_duration_minutes`.  
P/L: `revenue`, `expenses`, `profit`, `expenses_by_category: [{ category, total }]`.

Simple figures and one bar or stacked list for categories. No 3D charts.

---

## Forms and UI behavior

- React Hook Form + Zod on quote, review, login, job create, invoice create.
- TanStack Query for GET lists. Invalidate on create/convert/send.
- One `apiFetch` helper: JSON, Bearer, 401 refresh, throw with parsed `message`.
- Disabled submit buttons while in flight. Success and error as text under the form, not toast spam.
- Public site must work if the API is down: show “Reviews are unavailable right now” rather than a blank hero crash.
- `GET /api/v1/services` is **auth-only**. Home services stay **hardcoded** from the table above.

---

## What not to build

- Customer/property/service CRUD screens (lookups only)
- Payments and expenses screens
- Photo upload, chat, maps SDK (plain ordered stop list is enough)
- Signup / forgot password
- Role-based access (single owner)
- GraphQL, Firebase, fake in-memory backend as production
- Admin URL on `/admin` — use `/app`

---

## Build order

1. Tailwind tokens, fonts, `site.ts`, public layout, home (static).
2. Quote page → `POST /leads`.
3. Review form → `POST /reviews`; home reviews → `GET /reviews`.
4. `apiFetch` + login + token refresh + `/app` guard.
5. Leads table + convert.
6. Jobs list + create (customer/property/service dropdowns) + start/complete.
7. Routes generate + today.
8. Invoice create / get / send.
9. Analytics.
10. Reviews approve/unapprove + approve-by-id.

---

## Done when

- Public pages match the copy and the green/brown paper look.
- Quote and review hit the real API.
- Owner can log in, fail login cleanly, and use leads, jobs, routes, invoices, analytics.
- Phone and email live in one config file.
- No purple SaaS chrome, no Inter-only marketing page, no fake backend.

# Client Portal

This document describes the client-facing portal added to the AIS project.

Overview
- New blueprint: `portal` (routes under `/portal`)
-- Purpose: allow clients to log in and view invoices, payment history, and installment plans.
-- Admin owners can preview a client view using the Client Login/selection flow in the Admin UI (persistent server-side impersonation was removed to match the Figma behavior).

Routes
- `GET /portal` — client dashboard overview (totals, active installments)
- `GET /portal/invoices` — list of the client's invoices
- `GET /portal/invoices/<id>` — invoice detail and payment history
- `GET /portal/payments` — list of client payments
- `POST /portal/payments/add` — record a payment for a client's invoice (server-side validation)

Impersonation (admin)
- Persistent session-based impersonation was intentionally removed. Owners may still switch to a client view via the Client Login flow in the Admin UI ("View as Client" selection), which does not create a server-side impersonation session.

Security and Permissions
- Portal pages enforce client scope:
  - Logged-in clients only see their own invoices (matched by `User.username` == `Client.email`).
  - Owners can impersonate via session; impersonation is visible in the UI.
- Payment endpoint validates invoice ownership before recording a payment.
- IMPORTANT: This app uses session-based auth and has no CSRF protection currently. In production, add CSRF middleware and secure session cookies.

Payment Integration (future)
- Current behavior: client-side "Make Payment" records a payment internally (no gateway).
- Recommended integration steps for Stripe:
  1. Create a server-side `/portal/checkout` route that creates a Stripe Checkout Session with the invoice amount.
  2. Redirect client to Stripe Checkout and handle successful payments via webhook.
  3. On webhook success, create `Payment` rows and update `Invoice` status.
  4. Send email receipts.

Backfill & Data Migration
- The portal uses `Invoice.installments_display` and `Payment.installment_number` to present installment progress.
- If you want explicit `installment_number` values for historical payments, run a backfill script (I can provide one) that assigns numbers based on running totals.

Demo Credentials
----------------
- **Admin:**
  - Username: `admin`
  - Password: `admin123`

- **Client:**
  - Email: `client1@example.com`
  - Password: `clientpass`

These are the seeded demo accounts created by `seed.py`. Re-running `seed.py` will recreate these sample users and example data.

Files Added
- `app/routes_portal.py` — portal blueprint and routes
- `app/templates/portal/*` — portal templates
- `docs/CLIENT_PORTAL.md` — this document

Next Steps
- Optionally add a UI control in the clients list to impersonate clients (added already as a button in the Actions column).
- Add CSRF protection and secure session settings for production.
- Integrate a real payment gateway (Stripe recommended) and add webhook handling.


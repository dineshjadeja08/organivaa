# Organivaa

A mobile-first Next.js storefront and operations panel for a premium Indian botanical wellness brand, backed by a Flask and SQLAlchemy API.

## Run locally

```bash
npm install
copy .env.example .env.local
npm run dev
```

`npm run dev` seeds the local database when needed and starts both Flask and Next.js in one terminal. Open `http://localhost:3000`. Use `npm run dev:web` only when Flask is already running separately, and use `npm run build` for a production check.

The operations control centre is available at `/admin`. Product variants, uploads, checkout orders, refunds, fulfilments, verified reviews, batch evidence, analytics and the supporting operational records are persisted through Flask. See `backend/README.md` and `ADMIN.md` for API, authentication and production-hardening requirements.

The storefront catalog is read entirely from Flask; no static product fallback is shipped. Checkout and shipping run through end-to-end sandbox adapters by default so pricing, stock, orders, tracking and admin actions can be tested safely. Live payment and courier credentials must be supplied and their provider adapters/webhooks reviewed before accepting real orders.

Only order-matched, admin-approved reviews can be published. Batch data is public only after an evidence document is attached and the record is approved. Unverified health claims and certifications remain absent or explicitly marked as review-pending.

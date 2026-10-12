# Architecture

The App Router is server-first. Client components are limited to search, cart persistence, product selection, pincode state, filters and interactive admin forms. Presentation depends on normalized `Product` objects returned by Flask.

Flask owns the product catalog, variants, assets, orders, refunds, fulfilments, reviews, batch traces and analytics events. Next.js reads through server-only adapters or same-origin Route Handlers so service credentials never enter the browser. Claims remain separate governed records; production renders approved, in-date records only.

Cart presentation persists locally, while Flask recalculates authoritative prices, availability and shipping when creating checkout. A production payment adapter must use server-created provider orders, signed callbacks and idempotent webhooks.
# Application architecture

The customer storefront and operations interface run in Next.js. Browser admin mutations go through protected Next.js Route Handlers, which forward requests to Flask with a server-only service token. Flask owns validation, persistence and audit logging through SQLAlchemy.

Local development uses SQLite. Production uses PostgreSQL by setting `DATABASE_URL`; no frontend code changes are required. External checkout, payment, shipping, email, review and analytics providers remain explicit adapters and are not simulated as live services.

# Organivaa Operations Admin

The admin control centre lives at `/admin`. In local development, when no admin credentials are configured, it opens in an explicitly labelled development mode. Production fails closed and redirects to `/admin/login`.

## Production authentication

Set `ADMIN_PASSWORD` and a random `ADMIN_SESSION_SECRET` of at least 32 bytes. The included credential flow uses an HTTP-only, Strict SameSite, signed session cookie. For multiple administrators, MFA, password recovery and role-based access, replace it with a managed identity provider before launch.

## Data provider

The admin is backed by the Flask service in `backend/`. `src/lib/admin/store.ts` is a server-only adapter that forwards authenticated requests to Flask; the browser never receives the service token. SQLite is used locally and PostgreSQL is selected through `DATABASE_URL` in production.

Before production:

1. Configure PostgreSQL and rotate all development secrets.
2. Connect the catalog, checkout, payment and fulfilment providers through signed webhooks.
3. Keep service-token authorization inside every Next.js route adapter and Flask admin endpoint.
4. Add provider-specific idempotency keys, rate limiting and off-site audit exports before launch.
5. Replace the bootstrap operator with managed identity and MFA for multiple administrators.

The admin never collects or stores raw card numbers.

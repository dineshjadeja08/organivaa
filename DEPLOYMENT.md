# Deployment

Deploy the Next.js application to a compatible host and the Flask service behind TLS on the same private application network. Configure `.env.example` values, set `NEXT_PUBLIC_SITE_URL`, and run `npm run build` before promotion. Flask requires PostgreSQL, persistent object storage for uploads, strong secrets, and production payment/courier callbacks and webhooks. Do not expose the Flask service token to the browser.

Apply CSP and HSTS after all third-party origins are known. Never expose private tokens through `NEXT_PUBLIC_` variables.

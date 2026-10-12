# Environment

Copy `.env.example` to `.env.local`. Start the Flask API with `npm run backend` after seeding it once with `npm run backend:seed`. The Next.js storefront and admin use `FLASK_API_URL`; protected operations also use the server-only `FLASK_SERVICE_TOKEN`. Neither value is exposed to the browser. Flask uses SQLite locally and PostgreSQL through `DATABASE_URL`. Payment and shipping default to `sandbox`; production must fail deployment review until live provider credentials, signed callbacks and webhooks are configured and tested.

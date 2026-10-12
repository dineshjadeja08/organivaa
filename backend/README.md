# Organivaa Flask API

The Flask service is the durable operations layer for the Next.js storefront and admin panel. It uses SQLAlchemy with SQLite for local development and PostgreSQL when `DATABASE_URL` is configured.

## Local start

```powershell
python -m pip install -r backend/requirements.txt
python -m flask --app backend.run seed
python -m backend.run
```

The API starts on `http://127.0.0.1:5000`. The Next.js server expects:

```text
FLASK_API_URL=http://127.0.0.1:5000/api/v1
FLASK_SERVICE_TOKEN=organivaa-local-service-token
```

## Operations API

- `GET /api/v1/health`
- `GET /api/v1/catalog/products`
- `POST /api/v1/checkout/session` and `POST /api/v1/shipping/quote`
- `GET /api/v1/orders/<number>`
- `POST /api/v1/reviews` and `GET /api/v1/products/<handle>/reviews`
- `GET /api/v1/trace/<batch-code>`
- `POST /api/v1/analytics/events`
- `POST /api/v1/auth/login`
- `GET /api/v1/admin/summary`
- `GET|POST|PATCH|DELETE /api/v1/admin/<resource>`
- `GET|POST /api/v1/admin/catalog/products`
- `GET /api/v1/admin/orders` with refund and fulfilment actions
- review moderation, batch approval, uploads and analytics summary endpoints

Protected admin endpoints require `X-Service-Token`. Supported resources are products, orders, inventory, customers, content, claims, promotions, support, reviews and quality.

All creates, updates and deletes create immutable audit events. Raw payment card data is never accepted or stored.

Checkout and courier responses default to explicit sandbox adapters. Set provider credentials and replace the adapter calls before accepting live payments; the application never collects card data directly.

## Production

Set `FLASK_ENV=production`, a PostgreSQL `DATABASE_URL`, a random `SECRET_KEY`, a random `SERVICE_TOKEN`, and a strong bootstrap `ADMIN_PASSWORD`. Production startup fails when development secrets remain configured. Run behind TLS with Gunicorn or another WSGI host and restrict the Flask service to the application network.

The schema is SQLAlchemy/PostgreSQL compatible. Alembic is included for versioned production migrations; initialise a deployment migration environment against `organivaa_api.models.Base.metadata` before the first production rollout. Local development continues to bootstrap an isolated SQLite database for convenience.

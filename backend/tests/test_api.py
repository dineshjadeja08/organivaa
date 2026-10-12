from io import BytesIO

from backend.organivaa_api import create_app
from backend.organivaa_api.seed import seed_database


def app_client(tmp_path):
    app = create_app({"TESTING": True, "DATABASE_URL": f"sqlite:///{tmp_path / 'test.db'}", "SERVICE_TOKEN": "test-token", "ADMIN_EMAIL": "admin@test.local", "ADMIN_PASSWORD": "test-password"})
    with app.app_context():
        seed_database(app.config)
    return app.test_client()


def auth():
    return {"X-Service-Token": "test-token", "X-Operator": "pytest"}


def test_health_and_catalog(tmp_path):
    client = app_client(tmp_path)
    assert client.get("/api/v1/health").json["status"] == "ok"
    products = client.get("/api/v1/catalog/products").json["data"]
    assert products and products[0]["id"]


def test_admin_requires_service_token(tmp_path):
    client = app_client(tmp_path)
    assert client.get("/api/v1/admin/products").status_code == 401


def test_record_crud_and_audit(tmp_path):
    client = app_client(tmp_path)
    created = client.post("/api/v1/admin/content", headers=auth(), json={"id": "CNT-TEST", "title": "Test article", "subtitle": "Editorial", "status": "draft"})
    assert created.status_code == 201
    updated = client.patch("/api/v1/admin/content", headers=auth(), json={"id": "CNT-TEST", "status": "active"})
    assert updated.status_code == 200
    assert updated.json["data"]["status"] == "active"
    deleted = client.delete("/api/v1/admin/content", headers=auth(), json={"id": "CNT-TEST"})
    assert deleted.status_code == 200
    audit = client.get("/api/v1/admin/summary", headers=auth()).json["data"]["audit"]
    assert any("Deleted Test article" in event["title"] for event in audit)


def test_duplicate_and_invalid_status_are_rejected(tmp_path):
    client = app_client(tmp_path)
    duplicate = client.post("/api/v1/admin/products", headers=auth(), json={"id": "p1", "title": "Duplicate", "status": "active"})
    assert duplicate.status_code == 409
    invalid = client.patch("/api/v1/admin/products", headers=auth(), json={"id": "p1", "status": "magic"})
    assert invalid.status_code == 400


def test_checkout_order_review_and_refund_flow(tmp_path):
    client = app_client(tmp_path)
    product = client.get("/api/v1/catalog/products").json["data"][0]
    checkout = client.post("/api/v1/checkout/session", json={"name": "Test Customer", "email": "buyer@example.com", "address": {"pincode": "600001"}, "lines": [{"variantId": product["packs"][0]["id"], "quantity": 1}]})
    assert checkout.status_code == 201
    order = checkout.json["data"]["order"]
    tracked = client.get(f'/api/v1/orders/{order["number"]}?email=buyer@example.com')
    assert tracked.status_code == 200
    review = client.post("/api/v1/reviews", json={"handle": product["handle"], "orderNumber": order["number"], "email": "buyer@example.com", "author": "Buyer", "rating": 5, "title": "Simple ritual", "body": "The product information was clear and useful."})
    assert review.status_code == 201 and review.json["data"]["verifiedPurchase"] is True
    review_id = review.json["data"]["id"]
    assert client.patch(f"/api/v1/admin/reviews/{review_id}", headers=auth(), json={"status": "approved"}).status_code == 200
    assert len(client.get(f'/api/v1/products/{product["handle"]}/reviews').json["data"]) == 1
    assert client.post(f'/api/v1/admin/orders/{order["id"]}/refunds', headers=auth(), json={"amount": 100, "reason": "Test"}).status_code == 201


def test_upload_and_batch_traceability(tmp_path):
    client = app_client(tmp_path)
    product = client.get("/api/v1/catalog/products").json["data"][0]
    upload = client.post("/api/v1/admin/uploads", headers=auth(), data={"productId": product["id"], "alt": "Evidence document", "file": (BytesIO(b"%PDF-1.4 test"), "evidence.pdf")}, content_type="multipart/form-data")
    assert upload.status_code == 201
    created = client.post("/api/v1/admin/batches", headers=auth(), json={"productId": product["id"], "batchCode": "TEST-2026-01", "origin": "Tamil Nadu", "manufacturer": "Test Manufacturer", "manufacturedOn": "2026-01-10", "expiresOn": "2027-01-10", "reportAssetId": upload.json["data"]["id"]})
    assert created.status_code == 201
    batch = created.json["data"]
    assert client.get("/api/v1/trace/TEST-2026-01").status_code == 404
    assert client.patch(f'/api/v1/admin/batches/{batch["id"]}', headers=auth(), json={"status": "approved"}).status_code == 200
    traced = client.get("/api/v1/trace/TEST-2026-01")
    assert traced.status_code == 200 and traced.json["data"]["reportUrl"]


def test_shipping_and_analytics(tmp_path):
    client = app_client(tmp_path)
    assert client.post("/api/v1/shipping/quote", json={"pincode": "600001", "subtotal": 1200}).json["data"]["shipping"] == 0
    assert client.post("/api/v1/analytics/events", json={"name": "page_view", "sessionId": "test", "path": "/shop", "payload": {}}).status_code == 202
    summary = client.get("/api/v1/admin/analytics/summary", headers=auth()).json["data"]
    assert summary["events"]["page_view"] == 1

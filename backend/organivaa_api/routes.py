import json
from datetime import datetime, timezone

from flask import Blueprint, current_app, request
from sqlalchemy import func, select
from werkzeug.security import check_password_hash

from .auth import require_service
from .database import db_session
from .models import AuditEvent, Operator, Record

api = Blueprint("api", __name__)
RESOURCES = {"products", "orders", "inventory", "customers", "content", "claims", "promotions", "support", "reviews", "quality"}
STATUSES = {"active", "draft", "pending", "attention", "archived", "fulfilled", "approved", "rejected"}


def iso(value):
    return value.astimezone(timezone.utc).isoformat() if value else None


def ago(value):
    if not value:
        return "—"
    seconds = max(0, int((datetime.now(timezone.utc) - value.replace(tzinfo=value.tzinfo or timezone.utc)).total_seconds()))
    if seconds < 60:
        return "Just now"
    if seconds < 3600:
        return f"{seconds // 60} min ago"
    if seconds < 86400:
        return f"{seconds // 3600} hr ago"
    return f"{seconds // 86400} days ago"


def serialize(record):
    return {"id": record.external_id, "title": record.title, "subtitle": record.subtitle, "status": record.status, "value": record.value, "updated": ago(record.updated_at), "version": record.version, "payload": json.loads(record.payload or "{}")}


def audit(session, action, resource, record_id, summary, before=None, after=None):
    session.add(AuditEvent(actor=request.headers.get("X-Operator", "next-admin"), action=action, resource=resource, record_id=record_id, summary=summary, before=json.dumps(before) if before else None, after=json.dumps(after) if after else None))


@api.get("/health")
def health():
    session = db_session()
    try:
        session.execute(select(1))
        return {"status": "ok", "service": "organivaa-api", "database": "connected", "environment": current_app.config["ENVIRONMENT"]}
    finally:
        session.close()


@api.post("/auth/login")
def login():
    body = request.get_json(silent=True) or {}
    session = db_session()
    try:
        operator = session.scalar(select(Operator).where(Operator.email == str(body.get("email", "")).lower()))
        if not operator or operator.status != "active" or not check_password_hash(operator.password_hash, str(body.get("password", ""))):
            return {"error": "Invalid credentials"}, 401
        return {"data": {"id": operator.id, "email": operator.email, "role": operator.role}, "message": "Credentials verified. Use the server-to-server service token for admin API access."}
    finally:
        session.close()


@api.get("/admin/summary")
@require_service
def summary():
    session = db_session()
    try:
        rows = session.execute(select(Record.resource, Record.status, func.count()).group_by(Record.resource, Record.status)).all()
        counts = {}
        for resource, status, count in rows:
            counts.setdefault(resource, {})[status] = count
        latest = session.scalars(select(AuditEvent).order_by(AuditEvent.created_at.desc()).limit(20)).all()
        return {"data": {"counts": counts, "audit": [{"id": f"AUD-{event.id}", "title": event.summary, "subtitle": f"{event.actor} · {event.resource}/{event.record_id}", "status": "active", "updated": ago(event.created_at)} for event in latest]}}
    finally:
        session.close()


@api.route("/admin/<resource>", methods=["GET", "POST", "PATCH", "DELETE"])
@require_service
def admin_resource(resource):
    if resource not in RESOURCES:
        return {"error": "Unknown resource"}, 404
    session = db_session()
    try:
        if request.method == "GET":
            records = session.scalars(select(Record).where(Record.resource == resource).order_by(Record.updated_at.desc(), Record.id.desc())).all()
            return {"data": [serialize(record) for record in records], "provider": "flask-sqlalchemy"}
        body = request.get_json(silent=True) or {}
        if request.method == "POST":
            required = ["id", "title", "status"]
            if any(not str(body.get(field, "")).strip() for field in required) or body.get("status") not in STATUSES:
                return {"error": "id, title and a valid status are required"}, 400
            exists = session.scalar(select(Record).where(Record.resource == resource, Record.external_id == str(body["id"])))
            if exists:
                return {"error": "Record ID already exists"}, 409
            record = Record(resource=resource, external_id=str(body["id"]).strip(), title=str(body["title"]).strip(), subtitle=str(body.get("subtitle", "")).strip(), status=body["status"], value=str(body["value"]).strip() if body.get("value") else None, payload=json.dumps(body.get("payload") or {}))
            session.add(record);session.flush();audit(session, "create", resource, record.external_id, f"Created {record.title}", after=serialize(record));session.commit()
            return {"data": serialize(record)}, 201
        record_id = str(body.get("id", request.args.get("id", ""))).strip()
        record = session.scalar(select(Record).where(Record.resource == resource, Record.external_id == record_id))
        if not record:
            return {"error": "Not found"}, 404
        before = serialize(record)
        if request.method == "DELETE":
            session.delete(record);audit(session, "delete", resource, record_id, f"Deleted {record.title}", before=before);session.commit()
            return {"data": {"id": record_id, "deleted": True}}
        if "status" in body and body["status"] not in STATUSES:
            return {"error": "Invalid status"}, 400
        for field in ("title", "subtitle", "status", "value"):
            if field in body:
                setattr(record, field, str(body[field]).strip() if body[field] is not None else None)
        if "payload" in body:
            record.payload = json.dumps(body["payload"] or {})
        record.version += 1
        session.flush();after = serialize(record);audit(session, "update", resource, record_id, f"Updated {record.title}", before=before, after=after);session.commit()
        return {"data": serialize(record)}
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()

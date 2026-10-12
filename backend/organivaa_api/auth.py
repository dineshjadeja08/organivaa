import hmac
from functools import wraps

from flask import current_app, request


def require_service(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        supplied = request.headers.get("X-Service-Token", "")
        expected = current_app.config["SERVICE_TOKEN"]
        if not supplied or not hmac.compare_digest(supplied, expected):
            return {"error": "Unauthorized"}, 401
        return view(*args, **kwargs)

    return wrapped

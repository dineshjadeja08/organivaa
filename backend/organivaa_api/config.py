import os
from pathlib import Path


class Config:
    def __init__(self):
        root = Path(__file__).resolve().parents[1]
        environment = os.getenv("FLASK_ENV", "development")
        self.ENVIRONMENT = environment
        self.DEBUG = environment == "development"
        self.TESTING = False
        self.DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{root / 'organivaa.db'}")
        self.SECRET_KEY = os.getenv("SECRET_KEY", "organivaa-local-secret-change-before-production")
        self.SERVICE_TOKEN = os.getenv("SERVICE_TOKEN", "organivaa-local-service-token")
        self.ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "admin@organivaa.local")
        self.ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "change-me-before-production")
        self.PORT = int(os.getenv("PORT", "5000"))
        self.MAX_CONTENT_LENGTH = int(os.getenv("MAX_UPLOAD_BYTES", str(10 * 1024 * 1024)))
        self.PAYMENT_PROVIDER = os.getenv("PAYMENT_PROVIDER", "sandbox")
        self.SHIPPING_PROVIDER = os.getenv("SHIPPING_PROVIDER", "sandbox")

    @staticmethod
    def validate(config):
        if config["ENVIRONMENT"] == "production":
            insecure = {
                "SECRET_KEY": "organivaa-local-secret-change-before-production",
                "SERVICE_TOKEN": "organivaa-local-service-token",
                "ADMIN_PASSWORD": "change-me-before-production",
            }
            invalid = [key for key, value in insecure.items() if config.get(key) == value]
            if invalid:
                raise RuntimeError(f"Production secrets are not configured: {', '.join(invalid)}")

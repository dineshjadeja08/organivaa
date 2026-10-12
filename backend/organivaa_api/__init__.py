from flask import Flask

from .config import Config
from .database import close_session, init_database
from .routes import api
from .commerce_routes import commerce
from .seed import seed_database


def create_app(test_config: dict | None = None) -> Flask:
    app = Flask(__name__)
    app.config.from_object(Config())
    if test_config:
        app.config.update(test_config)
    Config.validate(app.config)
    init_database(app)
    app.register_blueprint(api, url_prefix="/api/v1")
    app.register_blueprint(commerce, url_prefix="/api/v1")
    app.teardown_appcontext(close_session)

    @app.get("/")
    def index():
        return {"service": "Organivaa API", "version": "1.0", "health": "/api/v1/health"}

    @app.cli.command("seed")
    def seed_command():
        count = seed_database(app.config)
        print(f"Organivaa database ready with {count} operation records.")

    @app.cli.command("reset-demo")
    def reset_demo_command():
        count = seed_database(app.config, force=True)
        print(f"Organivaa demo data reset with {count} operation records.")

    return app

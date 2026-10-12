from flask import current_app
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

from .models import Base

Session = scoped_session(sessionmaker(autoflush=False, expire_on_commit=False))


def init_database(app):
    url = app.config["DATABASE_URL"]
    options = {"check_same_thread": False} if url.startswith("sqlite") else {}
    engine = create_engine(url, future=True, pool_pre_ping=True, connect_args=options)
    Session.configure(bind=engine)
    Base.metadata.create_all(engine)
    app.extensions["organivaa_engine"] = engine


def close_session(_error=None):
    Session.remove()


def db_session():
    return Session()

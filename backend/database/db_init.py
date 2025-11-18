from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .models import Base
from config import Config
import os

_engine = None
_Session = None


def init_db(db_path=None):
    global _engine, _Session
    if db_path is None:
        db_uri = Config.SQLALCHEMY_DATABASE_URI
    else:
        db_uri = db_path
    _engine = create_engine(db_uri, echo=False, future=True)
    Base.metadata.create_all(_engine)
    _Session = sessionmaker(bind=_engine)


def get_session():
    if _Session is None:
        raise RuntimeError('Database not initialized. Call init_db() first.')
    return _Session()

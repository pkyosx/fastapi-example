import contextlib
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.orm import sessionmaker
from util.config_util import Config

engine = create_engine(Config.sqlalchemy_database_url, echo=True)

session_factory = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_engine():
    return engine


@contextlib.contextmanager
def create_session() -> Generator[Session, None, None]:
    session = session_factory()
    try:
        yield session
        session.commit()
    finally:
        session.close()

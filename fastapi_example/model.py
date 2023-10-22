from fastapi_example.util.sqlalchemy_util import get_engine
from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy.orm import declarative_base

BaseModel = declarative_base()


class Message(BaseModel):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True)
    content = Column(String)


def create_tables():
    engine = get_engine()
    BaseModel.metadata.create_all(engine)


def drop_tables():
    engine = get_engine()
    BaseModel.metadata.drop_all(engine)

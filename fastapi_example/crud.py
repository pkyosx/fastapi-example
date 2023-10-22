from model import Message
from sqlalchemy.orm import Session


def create_message(session: Session, content: str) -> Message:
    message = Message(content=content)
    session.add(message)
    session.flush()
    return message


def list_messages(session: Session, limit: int) -> list[Message]:
    return session.query(Message).limit(limit).all()

import uuid
from datetime import datetime
from sqlalchemy import Column, String, UUID, DateTime, Uuid
from sqlalchemy.orm import reconstructor
from sqlalchemy_utils import EmailType
from .pg_db import Base


class User(Base):
    __tablename__ = 'user'
    user_id  = Column(UUID, primary_key=True, default=uuid.uuid4)
    email = Column(EmailType, unique=True)

    def __init__(self, email: str):
        self.email = email


class Message(Base):
    __tablename__ = 'message'
    message_id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    email = Column(EmailType)
    date = Column(DateTime)
    topic = Column(String)
    from_email = Column(EmailType)
    message_text = Column(String)
    receive_date = Column(DateTime, default=datetime.now())

    def __init__(self, email: str, date: str, topic: str, from_email: str, message_text: str):
        self.email = email
        self.date = date
        self.topic = topic
        self.from_email = from_email
        self.message_text = message_text

    @reconstructor
    def on_load(self):
        self.date = self.date.isoformat() if isinstance(self.date, datetime) else self.date

    def to_dict(self):
        return {
            "email": self.email,
            "date": self.date,
            "topic": self.topic,
            "from_email": self.from_email,
            "message_text": self.message_text
        }




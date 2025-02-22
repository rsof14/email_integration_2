from sqlalchemy import Column, String, UUID, DateTime
from sqlalchemy_utils import EmailType
import uuid
from .pg_db import Base
from datetime import datetime


class User(Base):
    __tablename__ = 'user'
    user_id  = Column(UUID, primary_key=True, default=uuid.uuid4())
    email = Column(EmailType, unique=True)


class Message(Base):
    __tablename__ = 'message'
    message_id = Column(UUID, primary_key=True, default=uuid.uuid4())
    email = Column(EmailType)
    date = Column(DateTime)
    topic = Column(String)
    from_email = Column(EmailType)
    message_text = Column(String)
    receive_date = Column(DateTime, default=datetime.now())




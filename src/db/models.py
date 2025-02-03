from sqlalchemy import Column, String, UUID
from sqlalchemy_utils import EmailType
import uuid
from .pg_db import Base


class User(Base):
    __tablename__ = 'user'
    user_id  = Column(UUID, primary_key=True, default=uuid.uuid4())
    email = Column(EmailType, unique=True)


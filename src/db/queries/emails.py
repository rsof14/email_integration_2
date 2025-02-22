from sqlalchemy import desc
from sqlalchemy.orm import Session
from db.models import Message


def get_last_message(db: Session, email: str):
    return db.query(Message).filter_by(email=email).order_by(desc(Message.date)).first()

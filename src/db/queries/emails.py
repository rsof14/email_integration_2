from sqlalchemy import desc
from sqlalchemy.orm import Session
from src.db.models import Message


def get_last_message(db: Session, email: str):
    return db.query(Message).filter_by(email=email).order_by(desc(Message.date)).first()


def write_messages(db: Session, email: str, messages: list[dict]):
    for message in messages:
        msg = Message(email=email, date=message['date'], from_email=message['from_email'],
                              topic=message['topic'], message_text=message['message_text'])
        db.add(msg)
    db.commit()


def get_user_emails_page(db: Session, email: str, page_from: int, page_size: int):
    return db.query(Message).filter_by(email=email).order_by(desc(Message.date)).limit(page_size).offset(
        page_from).all()


def get_all_emails(db: Session, email: str):
    return db.query(Message).filter_by(email=email).all()

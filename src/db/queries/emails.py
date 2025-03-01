from sqlalchemy import desc
from sqlalchemy.orm import Session
from db.models import Message


def get_last_message(db: Session, email: str):
    return db.query(Message).filter_by(email=email).order_by(desc(Message.date)).first()


def write_messages(db: Session, email: str, messages: list[dict]):
    print(f'write messages {messages}')
    for message in messages:
        msg = Message(email=email, date=message['date'], from_email=message['from_email'],
                              topic=message['topic'], message_text=message['message_text'])
        print(msg.message_id)
        db.add(msg)
    db.commit()

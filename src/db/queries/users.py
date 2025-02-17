from sqlalchemy.orm import Session
from db.models import User


def get_user_by_email(db: Session, email: str):
    return db.query(User).filter_by(email=email).first()


def create_user(db: Session, email: str):
    user = get_user_by_email(db, email)
    if not user:
        new_user = User(email=email)
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
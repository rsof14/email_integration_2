from sqlalchemy.orm import Session
from db.models import User


def doest_user_exists(db: Session, email: str):
    return db.query(User).filter_by(email=email).first()


def update_user(db: Session, user: User, password: str):
    user.password = password
    db.commit()

# Создание пользователя
def create_user(db: Session, email: str, password: str):
    user = doest_user_exists(db, email)
    if user:
        update_user(db, user, password)
    else:
        new_user = User(email=email, password=password)
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
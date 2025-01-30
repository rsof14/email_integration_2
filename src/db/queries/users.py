from sqlalchemy.orm import Session
from db.models import User

# Создание пользователя
def create_user(db: Session, email: str, password: str):
    new_user = User(email=email, password=password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user
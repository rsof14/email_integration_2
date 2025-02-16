from api.models.login import LoginRequest
from db.queries.users import create_user
from .email_service import check_password


class UserIncorrectLoginData(Exception):
    ...


async def login_user(data: LoginRequest, db):
    if check_password(data.email, data.password):
        create_user(db, data.email)
        return {'email': data.email, 'password': data.password}
    else:
        raise UserIncorrectLoginData('Неверный логин или пароль')


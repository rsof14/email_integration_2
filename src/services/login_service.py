from api.models.login import LoginRequest
from db.queries.users import create_user
from .email_service import check_email_password


class UserIncorrectLoginData(Exception):
    ...


async def login_user(data: LoginRequest, db):
    if await check_email_password(data.email, data.password):
        create_user(db, data.email, data.password)
        return {'msg': 'User created'}
    raise UserIncorrectLoginData('Login or password is incorrect')

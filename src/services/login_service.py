from api.models.login import LoginRequest
from db.queries.users import create_user
from .email_service import check_password
from .passwords import create_access_token


class UserIncorrectLoginData(Exception):
    ...


async def login_user(data: LoginRequest, db):
    if check_password(data.email, data.password):
        create_user(db, data.email)
        token = create_access_token({'email': data.email, 'password': data.password})
        return {'access_token': token, 'token_type': 'Bearer'}
    else:
        raise UserIncorrectLoginData('Login or password is incorrect')


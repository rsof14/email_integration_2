from api.models.login import LoginRequest
from db.queries.users import create_user
from .email_service import GettingIMAPServerError, check_password
from imapclient.exceptions import LoginError
from .passwords import hash_password, create_access_token


class UserIncorrectLoginData(Exception):
    ...


async def login_user(data: LoginRequest, db):
    try:
        if check_password(data.email, data.password):
            # data.password = hash_password(data.password)
            create_user(db, data.email, data.password)
            token = create_access_token({'email': data.email})
            return {'access_token': token, 'token_type': 'Bearer'}
    except (GettingIMAPServerError, LoginError):
        raise UserIncorrectLoginData('Login or password is incorrect')


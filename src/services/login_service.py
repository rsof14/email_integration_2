from api.models.login import LoginRequest
from db.queries.users import create_user
from db.queries.emails import get_last_message
from .email_service import check_password, check_mailbox


class UserIncorrectLoginData(Exception):
    ...


async def login_user(data: LoginRequest, db):
    if check_password(data.email, data.password):
        last_message = get_last_message(db, data.email)
        since_date = last_message.date if last_message else None
        print(f'since date {since_date}')
        await check_mailbox(data.email, data.password, since_date)
        create_user(db, data.email)
        return {'email': data.email, 'password': data.password}
    else:
        raise UserIncorrectLoginData('Неверный логин или пароль')


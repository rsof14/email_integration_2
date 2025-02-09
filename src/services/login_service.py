from api.models.login import LoginRequest
from db.queries.users import create_user
from .email_service import check_password
import uuid
from db.redis_storage import get_redis
import orjson
from core.config import app_config


class UserIncorrectLoginData(Exception):
    ...


async def login_user(data: LoginRequest, db):
    if check_password(data.email, data.password):
        session_id = str(uuid.uuid4())
        create_user(db, data.email)
        redis_session = await get_redis()
        await redis_session.set(session_id, orjson.dumps({'email': data.email, 'password': data.password}),
                                ex=app_config.SESSION_TTL_DAYS * 24 * 60 * 60)
        return session_id
    else:
        raise UserIncorrectLoginData('Login or password is incorrect')


async def get_user_data_from_session(session_id: str | None):
    redis_session = await get_redis()
    session = await redis_session.get(session_id) if session_id else None
    return session

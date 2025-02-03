from datetime import timedelta, datetime
from jose import jwt, JWTError
from core.config import app_config


class IncorrectAccessToken(Exception):
    ...


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now() + expires_delta
    else:
        expire = datetime.now() + timedelta(minutes=app_config.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode["exp"] = expire
    encoded_jwt = jwt.encode(to_encode, app_config.JWT_SECRET_KEY, algorithm=app_config.JWT_ALGORITHM)
    return encoded_jwt


def decode_jwt(token: str):
    try:
        payload = jwt.decode(token, app_config.JWT_SECRET_KEY, algorithms=[app_config.JWT_ALGORITHM])
        return payload
    except JWTError:
        raise IncorrectAccessToken
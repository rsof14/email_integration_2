from fastapi import FastAPI
import uvicorn
from core.config import app_config
from api import login, emails
from fastapi.staticfiles import StaticFiles
from starsessions import SessionMiddleware
from starsessions.stores.redis import RedisStore
from db.redis_storage import get_redis


app = FastAPI(
    title=app_config.app_name
)

session_store = RedisStore(connection=get_redis())

app.add_middleware(SessionMiddleware, store=session_store, lifetime=3600 * 24 * app_config.SESSION_TTL_DAYS)

app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(login.router, prefix='/login', tags=['login'])
app.include_router(emails.router, prefix='/email', tags=['email'])


if __name__ == '__main__':
    uvicorn.run(
        'main:app',
        host=app_config.host,
        port=app_config.port
    )
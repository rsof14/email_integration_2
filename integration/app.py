from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starsessions import SessionMiddleware, SessionAutoloadMiddleware
from starsessions.stores.redis import RedisStore
from .api import login, emails
from .core.config import app_config
from .db.redis_storage import get_redis

app = FastAPI(
    title=app_config.app_name
)

session_store = RedisStore(connection=get_redis())

app.add_middleware(SessionAutoloadMiddleware)
app.add_middleware(SessionMiddleware, store=session_store, lifetime=3600 * 24 * app_config.SESSION_TTL_DAYS)


app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(login.router, prefix='/login', tags=['login'])
app.include_router(emails.router, prefix='/email', tags=['email'])

from fastapi import FastAPI
import uvicorn
from core.config import app_config
from api import login, emails
from fastapi.staticfiles import StaticFiles


app = FastAPI(
    title=app_config.app_name
)

app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(login.router, prefix='/login', tags=['login'])
app.include_router(emails.router, prefix='/email', tags=['email'])


if __name__ == '__main__':
    uvicorn.run(
        'main:app',
        host=app_config.host,
        port=app_config.port
    )
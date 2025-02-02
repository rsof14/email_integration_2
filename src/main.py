from fastapi import FastAPI
import uvicorn
from core.config import app_config
from api import login, emails


app = FastAPI(
    title=app_config.app_name
)

app.include_router(login.router, prefix='/api/login', tags=['login'])
app.include_router(emails.router, prefix='/api/emails', tags=['emails'])


if __name__ == '__main__':
    uvicorn.run(
        'main:app',
        host=app_config.host,
        port=app_config.port
    )
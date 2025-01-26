from fastapi import FastAPI
import uvicorn
from core.config import app_config
from api import login


app = FastAPI(
    title=app_config.app_name
)


app.include_router(login.router, prefix='/api/login', tags=['login'])


if __name__ == '__main__':
    uvicorn.run(
        'main:app',
        host=app_config.host,
        port=app_config.port
    )
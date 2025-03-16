import uvicorn
from integration.app import app   # in order for app to be in main module (main:app for uvicorn)
from integration.core.config import app_config


if __name__ == '__main__':
    uvicorn.run(
        'main:app',
        host=app_config.host,
        port=app_config.port
    )
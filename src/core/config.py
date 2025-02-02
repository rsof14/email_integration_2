from pydantic_settings import BaseSettings, SettingsConfigDict
import os
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class PGConfig(BaseSettings):
    model_config = SettingsConfigDict(env_file="../../.env")
    db_host: str
    db_port: int
    db_name: str
    db_schema: str
    db_user: str
    db_password: str


pg_config = PGConfig()


class AppConfig(BaseSettings):
    model_config = SettingsConfigDict(env_file="../../.env")
    app_name: str = "Email integration"
    host: str
    port: int
    SQLALCHEMY_DATABASE_URL: str = \
        f'postgresql://{pg_config.db_user}:{pg_config.db_password}@{pg_config.db_host}:{pg_config.db_port}/{pg_config.db_name}'
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str


app_config = AppConfig()
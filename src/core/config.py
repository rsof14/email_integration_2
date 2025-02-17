from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
import os
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class PGConfig(BaseSettings):
    model_config = SettingsConfigDict(env_file="../../.env")
    pg_host: str
    pg_port: int
    pg_name: str
    pg_schema: str
    pg_user: str
    pg_password: str


class RedisConfig(BaseSettings):
    model_config = SettingsConfigDict(env_file="../../.env")
    host: str = Field(validation_alias='redis_host')
    port: int = Field(validation_alias='redis_port')


pg_config = PGConfig()
redis_config = RedisConfig()


class AppConfig(BaseSettings):
    model_config = SettingsConfigDict(env_file="../../.env")
    app_name: str = "Email integration"
    host: str
    port: int
    SQLALCHEMY_DATABASE_URL: str = \
        f'postgresql://{pg_config.pg_user}:{pg_config.pg_password}@{pg_config.pg_host}:{pg_config.pg_port}/{pg_config.pg_name}'
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str
    SESSION_TTL_DAYS: int


app_config = AppConfig()
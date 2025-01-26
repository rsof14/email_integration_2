from pydantic_settings import BaseSettings, SettingsConfigDict
import os
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class AppConfig(BaseSettings):
    model_config = SettingsConfigDict(env_file="../../.env")
    app_name: str = "Email integration"
    host: str
    port: int


app_config = AppConfig()
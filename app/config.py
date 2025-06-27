from pydantic import ConfigDict
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    OPENAI_API_KEY: str
    DATA_PATH: str

    model_config = ConfigDict(env_file=".env")


settings = Settings()

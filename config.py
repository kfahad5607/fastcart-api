from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    APP_NAME: str = "FastCart API"
    DEBUG_MODE: bool = False
    DB_HOST: str = "localhost"
    DB_PORT: str = "5431"
    DB_NAME: str = "fastcartdb"
    DB_USER: str = "postgres"
    DB_PASSWORD: str = "postgres"
    DB_URL: str = ""

    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8')

settings = Settings()
settings.DB_URL = f"postgresql+asyncpg://{settings.DB_USER}:{settings.DB_PASSWORD}@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"
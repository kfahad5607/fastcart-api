from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "FastCart API"
    DEBUG_MODE: bool = False
    DB_HOST: str = "localhost"
    DB_PORT: str = "5432"
    DB_NAME: str = "fastcartdb"
    DB_USER: str = "postgres"
    DB_PASSWORD: str = "postgres"
    DB_URL: str = ""

    class Config:
        env_file = ".env"

settings = Settings()
settings.DB_URL = f"postgresql+asyncpg://{settings.DB_USER}:{settings.DB_PASSWORD}@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"
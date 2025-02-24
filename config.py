from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    APP_NAME: str = "FastCart API"
    DEBUG_MODE: bool = False
    CORS_ORIGINS: str = "http://localhost:5173"
    DB_HOST: str = "localhost"
    DB_PORT: str = "5432"
    DB_NAME: str = "fastcart_db"
    DB_USER: str = "postgres"
    DB_PASSWORD: str = "postgres"
    DB_URL: str = ""

    TEST_DB_HOST: str = "localhost"
    TEST_DB_PORT: str = "5433"
    TEST_DB_NAME: str = "test_db"
    TEST_DB_USER: str = "testuser"
    TEST_DB_PASSWORD: str = "testpass"
    TEST_DB_URL: str = ""

    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8')

settings = Settings()

settings.DB_URL = f"postgresql+asyncpg://{settings.DB_USER}:{settings.DB_PASSWORD}@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"
settings.TEST_DB_URL = f"postgresql+asyncpg://{settings.TEST_DB_USER}:{settings.TEST_DB_PASSWORD}@{settings.TEST_DB_HOST}:{settings.TEST_DB_PORT}/{settings.TEST_DB_NAME}"

settings.CORS_ORIGINS = list(map(lambda s: s.strip(), settings.CORS_ORIGINS.split(",")))
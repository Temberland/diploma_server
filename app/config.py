from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30
    AES_KEY: str  # 32 байта в hex
    ENVIRONMENT: str = "dev"

    class Config:
        env_file = ".env"


settings = Settings()

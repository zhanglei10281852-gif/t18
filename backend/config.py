import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DB_HOST: str = os.getenv("DB_HOST", "localhost")
    DB_PORT: int = int(os.getenv("DB_PORT", 3307))
    DB_USER: str = os.getenv("DB_USER", "agri_user")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "agri_pass")
    DB_NAME: str = os.getenv("DB_NAME", "agri_water")

    SECRET_KEY: str = os.getenv("SECRET_KEY", "agri-water-secret-key-2024")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 1440))

    BASE_QUOTA_PER_MU: float = 300.0

    @property
    def DATABASE_URL(self):
        return f"mysql+pymysql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}?charset=utf8mb4"


settings = Settings()

from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):

    # ===============================
    # DATABASE
    # ===============================
    DATABASE_URL: str

    # ===============================
    # OPENAI
    # ===============================
    OPENAI_API_KEY: str

    # ===============================
    # FIREBASE
    # ===============================
    FIREBASE_CREDENTIALS_PATH: str | None = None

    # ===============================
    # SECURITY KEYS
    # ===============================
    FACTORY_SECRET_KEY: str
    INTERNAL_CRON_SECRET: str
    ADMIN_INTERNAL_SECRET: str

    # ===============================
    # ENV
    # ===============================
    ENVIRONMENT: str = "development"

    # ===============================
    # FEATURE FLAGS
    # ===============================
    ENABLE_BOBOTV: bool = False

    # ===============================
    # AWS / S3 (BoboTV)
    # ===============================
    AWS_ACCESS_KEY_ID: str | None = None
    AWS_SECRET_ACCESS_KEY: str | None = None
    AWS_REGION: str = "us-east-1"
    AWS_S3_BUCKET_BOBOTV: str | None = None

    # Presigned URL lifetime in seconds (default 15 min)
    BOBOTV_PRESIGNED_URL_EXPIRY: int = 900

    # Max video upload size in MB
    BOBOTV_MAX_UPLOAD_SIZE_MB: int = 500

    class Config:
        env_file = ".env"
        extra = "ignore"
        case_sensitive = True


@lru_cache
def get_settings():
    return Settings()


settings = get_settings()
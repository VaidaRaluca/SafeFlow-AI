from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path

class Settings(BaseSettings):
    DATABASE_URL: str

    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    APP_NAME: str = "SafeFlow AI API"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    MODEL_DIR: Path = Path("app/ml_models")
    GLOBAL_MODEL_FILENAME: str = "isolation_forest_global.joblib"
    MODEL_PATH : Path = Path("app/ml_models/isolation_forest_global.joblib")


settings = Settings()
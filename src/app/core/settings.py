from pydantic import computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict
import os

class Settings(BaseSettings):
    # API name and version
    API_NAME: str = "Data Lineage Tracker"
    API_VERSION: str = "1.0.0"

    # Database configuration
    DATABASE_PORT: int = 5432
    DATABASE_HOST: str = "localhost"
    DATABASE_USER: str = "user"
    DATABASE_PASSWORD: str = "password"
    DATABASE_NAME: str = "dbname"
    TEST_DATABASE_NAME: str = "test_dbname"

    @computed_field
    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql+asyncpg://{self.DATABASE_USER}:{self.DATABASE_PASSWORD}@{self.DATABASE_HOST}:{self.DATABASE_PORT}/{self.DATABASE_NAME}"

    @computed_field
    @property
    def TEST_DATABASE_URL(self) -> str:
        return f"postgresql+asyncpg://{self.DATABASE_USER}:{self.DATABASE_PASSWORD}@{self.DATABASE_HOST}:{self.DATABASE_PORT}/{self.TEST_DATABASE_NAME}"

    model_config = SettingsConfigDict(
        env_file=os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), ".env"), 
        env_file_encoding="utf-8"
    )

settings = Settings()

def get_settings() -> Settings:
    return settings


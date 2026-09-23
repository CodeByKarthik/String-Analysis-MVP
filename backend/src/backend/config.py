from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_version: str = Field(validation_alias="APP_VERSION")
    api_host: str = Field(validation_alias="API_HOST")
    api_port: int = Field(validation_alias="API_PORT")

    model_config = SettingsConfigDict(
        env_file=Path(__file__).resolve().parents[3] / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()  # type: ignore[call-arg]

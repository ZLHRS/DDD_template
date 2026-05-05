import os
from pathlib import Path

from pydantic import BaseModel, Field, SecretStr
from pydantic_settings import (
    BaseSettings,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
    YamlConfigSettingsSource,
)


class PostgresConfig(BaseModel):
    host: str
    port: int = Field(gt=0, lt=65536)
    user: str
    password: SecretStr
    db: str
    echo: bool = False
    pool_size: int = Field(default=30, ge=1)
    pool_timeout: int = Field(default=30, ge=0)
    pool_recycle: int = Field(default=3600, ge=0)
    max_overflow: int = Field(default=20, ge=0)
    pool_pre_ping: bool = True
    echo_pool: bool = False

    def get_url(self) -> str:
        return (
            "postgresql+asyncpg://"
            f"{self.user}:{self.password.get_secret_value()}@{self.host}:{self.port}/{self.db}"
        )


class AuthConfig(BaseModel):
    secret_key: SecretStr = Field(min_length=32)
    algorithm: str = Field(min_length=1)
    access_token_expire_minutes: int = Field(gt=0)
    refresh_token_expire_days: int = Field(gt=0)


class Config(BaseSettings):
    postgres: PostgresConfig
    auth: AuthConfig
    environment: str = Field(default="development", min_length=1)

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
        env_ignore_empty=True,
        extra="ignore",
        yaml_file="config.yaml",
    )

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        return (
            init_settings,
            env_settings,
            dotenv_settings,
            YamlConfigSettingsSource(settings_cls),
            file_secret_settings,
        )


def load_config() -> Config:
    file_name = os.environ.get("CONFIG_PATH", "config.yaml")
    file_path = Path(file_name)
    if not file_path.is_file():
        raise FileNotFoundError(f"Config file '{file_name}' not found")

    if file_name == "config.yaml":
        return Config()

    class ConfigFromFile(Config):
        model_config = SettingsConfigDict(
            **{**Config.model_config, "yaml_file": file_name}
        )

    return ConfigFromFile()

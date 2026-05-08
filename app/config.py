from pydantic import AliasChoices, BaseModel, Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


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


class EnvConfig(BaseSettings):
    db_host: str = Field(validation_alias=AliasChoices("DB_HOST", "POSTGRES__HOST"))
    db_port: int = Field(
        default=5432,
        gt=0,
        lt=65536,
        validation_alias=AliasChoices("DB_PORT", "POSTGRES__PORT"),
    )
    db_user: str = Field(validation_alias=AliasChoices("DB_USER", "POSTGRES__USER"))
    db_password: SecretStr = Field(
        validation_alias=AliasChoices("DB_PASSWORD", "POSTGRES__PASSWORD")
    )
    db_name: str = Field(validation_alias=AliasChoices("DB_NAME", "POSTGRES__DB"))
    db_echo: bool = Field(
        default=False,
        validation_alias=AliasChoices("DB_ECHO", "POSTGRES__ECHO"),
    )
    db_pool_size: int = Field(
        default=30,
        ge=1,
        validation_alias=AliasChoices("DB_POOL_SIZE", "POSTGRES__POOL_SIZE"),
    )
    db_pool_timeout: int = Field(
        default=30,
        ge=0,
        validation_alias=AliasChoices("DB_POOL_TIMEOUT", "POSTGRES__POOL_TIMEOUT"),
    )
    db_pool_recycle: int = Field(
        default=3600,
        ge=0,
        validation_alias=AliasChoices("DB_POOL_RECYCLE", "POSTGRES__POOL_RECYCLE"),
    )
    db_max_overflow: int = Field(
        default=20,
        ge=0,
        validation_alias=AliasChoices("DB_MAX_OVERFLOW", "POSTGRES__MAX_OVERFLOW"),
    )
    db_pool_pre_ping: bool = Field(
        default=True,
        validation_alias=AliasChoices("DB_POOL_PRE_PING", "POSTGRES__POOL_PRE_PING"),
    )
    db_echo_pool: bool = Field(
        default=False,
        validation_alias=AliasChoices("DB_ECHO_POOL", "POSTGRES__ECHO_POOL"),
    )
    auth_secret_key: SecretStr = Field(
        min_length=32,
        validation_alias=AliasChoices("AUTH_SECRET_KEY", "AUTH__SECRET_KEY"),
    )
    auth_algorithm: str = Field(
        min_length=1,
        validation_alias=AliasChoices("AUTH_ALGORITHM", "AUTH__ALGORITHM"),
    )
    auth_access_token_expire_minutes: int = Field(
        gt=0,
        validation_alias=AliasChoices(
            "AUTH_ACCESS_TOKEN_EXPIRE_MINUTES",
            "AUTH__ACCESS_TOKEN_EXPIRE_MINUTES",
        ),
    )
    auth_refresh_token_expire_days: int = Field(
        gt=0,
        validation_alias=AliasChoices(
            "AUTH_REFRESH_TOKEN_EXPIRE_DAYS",
            "AUTH__REFRESH_TOKEN_EXPIRE_DAYS",
        ),
    )
    environment: str = Field(default="development", min_length=1)

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_ignore_empty=True,
        extra="ignore",
    )


class Config(BaseModel):
    postgres: PostgresConfig
    auth: AuthConfig
    environment: str = Field(default="development", min_length=1)


def load_config() -> Config:
    env_config = EnvConfig()
    return Config(
        postgres=PostgresConfig(
            host=env_config.db_host,
            port=env_config.db_port,
            user=env_config.db_user,
            password=env_config.db_password,
            db=env_config.db_name,
            echo=env_config.db_echo,
            pool_size=env_config.db_pool_size,
            pool_timeout=env_config.db_pool_timeout,
            pool_recycle=env_config.db_pool_recycle,
            max_overflow=env_config.db_max_overflow,
            pool_pre_ping=env_config.db_pool_pre_ping,
            echo_pool=env_config.db_echo_pool,
        ),
        auth=AuthConfig(
            secret_key=env_config.auth_secret_key,
            algorithm=env_config.auth_algorithm,
            access_token_expire_minutes=env_config.auth_access_token_expire_minutes,
            refresh_token_expire_days=env_config.auth_refresh_token_expire_days,
        ),
        environment=env_config.environment,
    )

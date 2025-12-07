from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    db_host: str
    db_user: str
    db_password: str
    db_port: int
    db_database: str

    model_config = SettingsConfigDict(
        env_file = ".env"
    )

settings = Settings()
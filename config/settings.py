from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    db_host: str
    db_user: str
    db_password: str
    db_port: int
    db_database: str

    whatsapp_app_id: str
    whatsapp_app_secret: str
    whatsapp_app_version: str
    webhook_verify_token: str

    model_config = SettingsConfigDict(
        env_file = ".env"
    )

settings = Settings()
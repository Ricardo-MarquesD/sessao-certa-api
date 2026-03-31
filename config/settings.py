from pydantic import Field, AliasChoices
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

    google_client_id: str
    google_client_secret: str = Field(
        validation_alias=AliasChoices("GOOGLE_CLIENT_SECRET", "GOOGLE_CLIENT"),
        default="",
    )
    google_redirect_uri: str | None = None
    google_auth_uri: str = "https://accounts.google.com/o/oauth2/v2/auth"
    google_token_uri: str = "https://oauth2.googleapis.com/token"
    google_calendar_scopes: str = "https://www.googleapis.com/auth/calendar.events"

    model_config = SettingsConfigDict(
        env_file = ".env"
    )

settings = Settings()
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

    brevo_api_secret: str = Field(
        validation_alias=AliasChoices(
            "BREVO_API_SECRET",
            "BREVO_API_KEY",
            "BREEVO_API_KEY",
            "brevo_api_secret",
            "brevo_api_key",
            "breevo_api_key",
        ),
        default="",
    )

    stripe_api_key: str = Field(
        validation_alias=AliasChoices("STRIPE_API_KEY", "STRIPE_SECRET_KEY", "stripe_api_key", "stripe_secret_key"),
        default="",
    )
    stripe_webhook_secret_instant: str = Field(
        validation_alias=AliasChoices(
            "STRIPE_WEBHOOK_SECRET_INSTANT",
            "STRIPE_WEBHOOK_INSTANT",
            "stripe_webhook_secret_instant",
            "stripe_webhook_instant",
        ),
        default="",
    )
    stripe_webhook_secret_minimum: str = Field(
        validation_alias=AliasChoices(
            "STRIPE_WEBHOOK_SECRET_MINIMUM",
            "STRIPE_WEBHOOK_MINIMUM",
            "stripe_webhook_secret_minimum",
            "stripe_webhook_minimum",
        ),
        default="",
    )
    
    model_config = SettingsConfigDict(
        env_file = ".env",
        extra = "allow",
    )

settings = Settings()
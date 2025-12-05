from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database: str
    password_database: str
    root: str
    port: int

    class Config:
        env_file = ".env"

settings = Settings()
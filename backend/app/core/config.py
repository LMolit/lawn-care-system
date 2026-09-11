from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str
    jwt_secret: str
    jwt_access_expire_minutes: int = 30
    jwt_refresh_expire_days: int = 30
    openrouteservice_api_key: str
    email_api_key: str
    email_from_address: str
    business_name: str = "Liberty Lawn Care"

    class Config:
        env_file = ".env"

settings = Settings()

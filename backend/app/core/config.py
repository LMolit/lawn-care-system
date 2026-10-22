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
    cors_origins: str = "http://localhost:3000"
    business_timezone: str = "America/Chicago"
    # Where "new lead" and "new review" alerts go. Blank turns alerts off.
    owner_alert_email: str = ""
    # Public address of the site, used for the links inside alert emails.
    site_url: str = "https://libertylawncarebatavia.com"

    class Config:
        env_file = ".env"


settings = Settings()

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    SCRAPE_URLS: str
    DATABASE_URL: str
    GEOCODE_API: str

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


env = Settings()

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    SCAPE_URL: str
    DATABASE_URL: str

    class Config:
        env_file = ".env"


env = Settings()

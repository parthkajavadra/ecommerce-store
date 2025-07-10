import os
from pydantic import BaseSettings

class Settings(BaseSettings):
    STRIPE_SECRET_KEY: str = os.getenv("STRIPE_SECRET_KEY", "your_secret_key_here")
    STRIPE_PUBLISHABLE_KEY: str = os.getenv("STRIPE_PUBLISHABLE_KEY", "your_publishable_key_here")

    class Config:
        env_file = ".env"

settings = Settings()

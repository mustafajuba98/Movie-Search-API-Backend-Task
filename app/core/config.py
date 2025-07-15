from pydantic_settings import BaseSettings, SettingsConfigDict 
from functools import lru_cache


class Settings(BaseSettings):
    OMDB_API_KEY: str
    TMDB_API_KEY: str
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8')

@lru_cache()

def get_settings() -> Settings:
    try:
        settings = Settings()
        return settings
    except Exception as e:
        print("Could not load .env file or settings")
        print(f"Error details: {e}")
        raise

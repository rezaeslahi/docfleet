from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="USER_", extra="ignore")
    service_name: str = Field(default="user-service")
    log_level: str = Field(default="INFO")

settings = Settings()
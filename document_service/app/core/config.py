from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="DOC_", extra="ignore")
    service_name: str = Field(default="document-service")
    log_level: str = Field(default="INFO")

settings = Settings()
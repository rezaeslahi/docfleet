from pydantic_settings import SettingsConfigDict, BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="GW_", extra="ignore")
    log_level: str = Field(default="INFO")

    # local address for internal 
    user_service_url: str = Field(default="http://localhost:8001")
    document_service_url: str = Field(default="http://localhost:8002")
    downloader_service_url: str = Field(default="http://localhost:8003")

    ml_service_url: str = Field(default="http://localhost:8004")
    default_search_n: int = Field(default=5, ge=1, le=50)
    max_search_n: int = Field(default=50, ge=1, le=200)

    # ML request shaping / safety
    ml_max_docs_to_rank: int = Field(default=200, ge=1, le=2000)
    ml_max_text_chars: int = Field(default=10_000, ge=200, le=200_000)



    http_timeout_seconds: float = Field(default=3.0)
    http_retries: int = Field(default=2)

settings = Settings()
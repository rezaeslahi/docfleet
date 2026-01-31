from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="ML_", extra="ignore")

    service_name: str = Field(default="ml-service")
    log_level: str = Field(default="INFO")

    # MLflow
    mlflow_tracking_uri: str = Field(default="http://127.0.0.1:5000")
    registered_model_name: str = Field(default="docfleet-relevance-model")
    model_alias: str = Field(default="champion")
    max_text_chars: int = Field(default=10_000, ge=200, le=200_000)


    # Safety limits
    max_docs_per_request: int = Field(default=200, ge=1, le=2000)


settings = Settings()

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[1]
# → /home/reza/projects/docfleet/downloader_service


DATA_DIR = BASE_DIR / "data"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="DL", extra="ignore")
    log_level:str = Field(default="INFO")

    data_dir:str = Field(default=str(DATA_DIR))

    time_out: float = Field(default=10,gt=0)
    max_concurrency:int = Field(default=5)

settings = Settings()
from pydantic import BaseModel, Field
from enum import Enum
from typing import List
import yaml

class PipelineMode(str,Enum):
    pandas = "pandas"
    spark = "spark"

class MissingValyeStrategy(str,Enum):
    fill = "fill"
    drop = "drop"



class ProjectConfig(BaseModel):
    experiment_name: str = Field(default="decfleet-relevance")
    registered_model_name: str = Field(default="docfleet-relevance-model")
    alias_for_best: str = Field(default="alias_for_best")

class PipelineConfig(BaseModel):
    mode: PipelineMode = Field(default=PipelineMode.pandas)

class DataConfig(BaseModel):
    negative_sampling_ratio: int = Field(default=2)
    test_size: float = Field(default=0.2)
    random_seed: int = Field(default=42)
    mising_value_method: MissingValyeStrategy = Field(default=MissingValyeStrategy.drop)

class FeaturesConfig(BaseModel):
   max_features: int = Field(default=4000)
   ngram_min: int = Field(default=1)
   ngram_max: int = Field(default=2)

class ModelConfig(BaseModel):
    grid_C: List[float] = Field(default_factory=lambda: [0.1, 0.5, 1.0, 2.0])
    max_iter: int = Field(default=500)

class MLConfig(BaseModel):
    project: ProjectConfig
    pipeline: PipelineConfig
    data: DataConfig
    features: FeaturesConfig
    model: ModelConfig

def create_ml_config(config_path:str)->MLConfig:
    with open(config_path, "r", encoding="utf-8") as f:
        raw = yaml.safe_load(f)
    ml_config = MLConfig(**raw)
    return ml_config


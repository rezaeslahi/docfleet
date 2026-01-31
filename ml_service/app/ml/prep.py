import pandas as pd
from dataclasses import dataclass
from abc import ABC, abstractmethod
from typing import Tuple
from enum import Enum
from app.core.train_config import MissingValyeStrategy

class MissingValueHandler(ABC):
    
    def __init__(self,method:MissingValyeStrategy):        
        super().__init__()
        self.strategy = method

    @abstractmethod
    def transform(self,df:pd.DataFrame)->pd.DataFrame:
        pass
    
    def is_data_ok(self,df:pd.DataFrame)->bool:
        is_ok = False
        if not df.isna().any().any():
            is_ok = True
        return is_ok

class DropMissingValue(MissingValueHandler):
    def __init__(self):
        super().__init__(MissingValyeStrategy.drop)
    
    def transform(self, df:pd.DataFrame)->pd.DataFrame:
        if self.is_data_ok(df): return df
        return df.dropna()

class FillMissingValue(MissingValueHandler):
    def __init__(self):
        super().__init__(MissingValyeStrategy.fill)
    
    def transform(self, df:pd.DataFrame)->pd.DataFrame:
        if self.is_data_ok(df): return df
        df = df.copy()

        # strings / objects -> ""
        str_cols = df.select_dtypes(include=["object", "string"]).columns
        df[str_cols] = df[str_cols].fillna("")

        # numbers -> 0
        num_cols = df.select_dtypes(include=["number"]).columns
        df[num_cols] = df[num_cols].fillna(0)

        # booleans -> False
        bool_cols = df.select_dtypes(include=["bool"]).columns
        df[bool_cols] = df[bool_cols].fillna(False)

def create_missing_value_handler(method: MissingValyeStrategy)->MissingValueHandler:
    if method == MissingValyeStrategy.drop:
        return DropMissingValue()
    elif method == MissingValyeStrategy.fill:
        return FillMissingValue()
    else:
        raise ValueError(f"Unkown missing value strategy: {method}")

@dataclass
class TextPairBuilder:
    sep: str = " [SEP] "

    def transform(self, df: pd.DataFrame) -> Tuple[pd.Series, pd.Series]:
        X = (df["query"] + self.sep + df["doc_text"]).astype(str)
        y = df["label"].astype(int)
        return X, y

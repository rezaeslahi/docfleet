from typing import List, Optional
from pydantic import BaseModel, Field


class DocIn(BaseModel):
    id: int
    title: str
    text: str
    tags: List[str] = Field(default_factory=list)


class RankRequest(BaseModel):
    query: str = Field(min_length=1, max_length=2000)
    docs: List[DocIn] = Field(min_length=1, max_length=2000)


class RankedDoc(BaseModel):
    id: int
    score: float
    title: Optional[str] = None


class RankResponse(BaseModel):
    query: str
    results: List[RankedDoc]

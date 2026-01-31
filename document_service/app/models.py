from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class DocumentBase(BaseModel):
    title: str = Field(...,min_length=3,max_length=200, description="This is document title")
    text: str = Field(...,min_length=1, max_length=200_000, description="This is document body")
    source_url: Optional[str] = Field(None,max_length=200, description="url")
    tags: List[str] = Field(default_factory=list, max_length=20)
    created_at: Optional[datetime] = Field(None)

class DocumentCreate(DocumentBase):
    pass

class Document(DocumentBase):
    id : int = Field(...,ge=1, description="This doc unique id")

class IngestRequest(BaseModel):
    documents: List[DocumentCreate] = Field(min_length=1, max_length=100)




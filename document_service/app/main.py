from .models import DocumentCreate, Document,IngestRequest
from .store import doc_store
from fastapi import FastAPI, HTTPException, status
from typing import List, Optional
import logging
from .core.logging import setup_logging
from .core.config import settings
from .core.request_id import request_id_middleware
import uvicorn

setup_logging()
logger = logging.getLogger(__name__)

app = FastAPI(title="This is document service", version="0.1.0")
app.middleware("http")(request_id_middleware)


@app.get("/health")
async def health()->dict:
    return {"status":"ok"}


@app.get("/document/{doc_id}", response_model=Document)
async def get_doc(doc_id: int)->Document:
    doc = doc_store.get_doc(doc_id)
    if doc is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Doc not found!")
    return doc

@app.get("/document",response_model=List[Document])
async def get_docs(first_n:Optional[int] = None)->List[Document]:
    docs = doc_store.list_documents(first_n=first_n)
    return docs

@app.post("/documents/ingest", response_model=List[Document], status_code=status.HTTP_201_CREATED)
async def ingest_documents(igest_docs: IngestRequest)->List[Document]:
    logger.info("ingest requested count=%s", len(igest_docs.documents))
    stored = doc_store.ingest_many(docs=igest_docs.documents)
    return stored

def run_server():
    uvicorn.run(
        app="app.main:app",
        port=8002,
        host="0.0.0.0",
        reload=True
    )    

if __name__ == "__main__":
    run_server()



from fastapi import FastAPI
from app.core.request_id import request_id_middleware
from app.api.routes_users import router as user_router
from app.api.routes_documents import router as document_router
from app.api.routes_ingest import router as ingest_router
from app.core.logging import setup_logging
from app.api.routes_search import router as search_router
import logging
import uvicorn

setup_logging()
logger = logging.getLogger(__name__)


app = FastAPI(title="DocFleet API Gateway", version="0.1.0")
app.middleware("http")(request_id_middleware)

app.include_router(user_router)
app.include_router(document_router)
app.include_router(ingest_router)
app.include_router(search_router)

@app.get("/health")
async def health()->dict:
    return {"status":"ok"}


def run_server():
    uvicorn.run(
        app="main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )


if __name__ == "__main__":
    run_server()

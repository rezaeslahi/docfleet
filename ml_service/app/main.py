import logging

from fastapi import FastAPI

from app.core.logging import setup_logging
from app.core.request_id import request_id_middleware
from app.api.routes_rank import router as rank_router

setup_logging()
logger = logging.getLogger(__name__)

app = FastAPI(title="DocFleet ML Service", version="0.1.0")
app.middleware("http")(request_id_middleware)

app.include_router(rank_router)


@app.get("/health")
async def health() -> dict:
    return {"status": "ok"}

from fastapi import HTTPException
from app.ml.model_loader import load_champion_model

@app.post("/model/refresh")
async def refresh_model() -> dict:
    try:
        _, v = load_champion_model(force_reload=True)
        return {"status": "reloaded", "version": v}
    except Exception as e:
        raise HTTPException(status_code=503, detail=str(e))


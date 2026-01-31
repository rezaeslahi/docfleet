import logging
from typing import List

from fastapi import APIRouter, HTTPException, Request

from app.core.config import settings
from app.ml.model_loader import load_champion_model
from app.ml.schemas import RankRequest, RankResponse, RankedDoc

router = APIRouter(tags=["rank"])
logger = logging.getLogger(__name__)


@router.post("/rank", response_model=RankResponse)
async def rank(payload: RankRequest, request: Request) -> RankResponse:
    request_id = request.state.request_id

    if len(payload.docs) > settings.max_docs_per_request:
        raise HTTPException(status_code=413, detail="Too many documents in one request")

    try:
        model, model_version = load_champion_model()
        logger.info("rank_request request_id=%s model_version=%s docs=%d",
            request_id, model_version, len(payload.docs))

    except Exception as e:
        logger.exception("model_load_failed request_id=%s", request_id)
        raise HTTPException(status_code=503, detail=f"Model not available: {e}")

    # Build feature strings exactly like training: "query [SEP] doc_text"
    X: List[str] = []
    for d in payload.docs:
        text = d.text
        if len(text) > settings.max_text_chars:
            text = text[: settings.max_text_chars]
        X.append(f"{payload.query} [SEP] {d.title}\n{text}")


    try:
        probs = model.predict_proba(X)[:, 1]  # probability of class=1 (relevant)
    except Exception as e:
        logger.exception("inference_failed request_id=%s", request_id)
        raise HTTPException(status_code=500, detail=f"Inference failed: {e}")

    ranked = sorted(
        [
            RankedDoc(id=d.id, title=d.title, score=float(p))
            for d, p in zip(payload.docs, probs)
        ],
        key=lambda r: r.score,
        reverse=True,
    )

    return RankResponse(query=payload.query, results=ranked)

from typing import Any, Dict, List

from fastapi import APIRouter, HTTPException, Query, Request

from app.clients.doc_client import list_documents
from app.clients.ml_client import rank_docs
from app.core.config import settings
from app.core.doc_adapter import adapt_docs_for_ml


router = APIRouter(tags=["search"])


@router.get("/search")
async def search(
    query: str = Query(min_length=1, max_length=2000),
    n: int = Query(default=settings.default_search_n, ge=1),
    request: Request = None,
) -> Dict[str, Any]:
    request_id = request.state.request_id

    # enforce max to avoid huge payloads
    n = min(n, settings.max_search_n)

    # 1) get docs from document service
    raw_docs = await list_documents(request_id=request_id)

    if not isinstance(raw_docs, list) or len(raw_docs) == 0:
        raise HTTPException(status_code=502, detail="Document service returned no documents")

    docs_for_ml, meta = adapt_docs_for_ml(raw_docs)

    if len(docs_for_ml) == 0:
        raise HTTPException(status_code=502, detail="No usable documents to rank")

    ranked = await rank_docs(request_id=request_id, query=query, docs=docs_for_ml)
    results: List[Dict[str, Any]] = ranked.get("results", [])
    top = results[:n]

    return {
        "query": query,
        "n": n,
        "total_docs": len(raw_docs),
        "meta": meta,
        "results": top, 
    }

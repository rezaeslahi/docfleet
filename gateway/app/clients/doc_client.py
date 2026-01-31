import asyncio
from typing import Any, Dict, Optional

import httpx
from fastapi import HTTPException

from app.core.config import settings
from app.core.request_id import REQUEST_ID_HEADER


async def _request_with_retries(
    method: str,
    url: str,
    request_id: str,
    json: Optional[Dict[str, Any]] = None,
    params: Optional[Dict[str,Any]] = None
) -> httpx.Response:
    timeout = httpx.Timeout(settings.http_timeout_seconds)

    last_exc: Exception | None = None
    for attempt in range(settings.http_retries + 1):
        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                resp = await client.request(
                    method,
                    url,
                    headers={REQUEST_ID_HEADER: request_id},
                    json=json,
                )
                return resp
        except (httpx.TimeoutException, httpx.TransportError) as e:
            last_exc = e
            if attempt < settings.http_retries:
                await asyncio.sleep(0.1 * (attempt + 1))
                continue
            break

    raise HTTPException(status_code=502, detail=f"Document service unavailable: {last_exc}")


async def list_documents(request_id: str, first_n: Optional[int] = None) -> Any:
    params: Dict[str,Any] = {}
    if first_n is not None:
        params["first_n":first_n]
    
    resp = await _request_with_retries("GET", f"{settings.document_service_url}/document", request_id,params=params)
    if resp.status_code != 200:
        raise HTTPException(status_code=resp.status_code, detail=resp.text)
    return resp.json()


async def get_document(doc_id: int, request_id: str) -> Any:
    resp = await _request_with_retries("GET", f"{settings.document_service_url}/document/{doc_id}", request_id)
    if resp.status_code == 404:
        raise HTTPException(status_code=404, detail="Document not found")
    if resp.status_code != 200:
        raise HTTPException(status_code=resp.status_code, detail=resp.text)
    return resp.json()

async def ingest_documents(request_id: str, documents_payload: Dict[str, Any]) -> Any:
    resp = await _request_with_retries(
        "POST",
        f"{settings.document_service_url}/documents/ingest",
        request_id,
        json=documents_payload,
    )
    if resp.status_code == 422:
        raise HTTPException(status_code=422, detail=resp.json())
    if resp.status_code != 201:
        raise HTTPException(status_code=resp.status_code, detail=resp.text)
    return resp.json()

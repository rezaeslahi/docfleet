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
    params: Optional[Dict[str, Any]] = None,
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
                    params=params,
                )
                return resp
        except (httpx.TimeoutException, httpx.TransportError) as e:
            last_exc = e
            if attempt < settings.http_retries:
                await asyncio.sleep(0.1 * (attempt + 1))
                continue
            break

    raise HTTPException(status_code=502, detail=f"ML service unavailable: {last_exc}")


async def rank_docs(request_id: str, query: str, docs: list[dict]) -> Dict[str, Any]:
    payload = {"query": query, "docs": docs}

    resp = await _request_with_retries(
        "POST",
        f"{settings.ml_service_url}/rank",
        request_id,
        json=payload,
    )

    if resp.status_code == 422:
        # validation error from ML service
        raise HTTPException(status_code=422, detail=resp.json())

    if resp.status_code != 200:
        raise HTTPException(status_code=resp.status_code, detail=resp.text)

    return resp.json()

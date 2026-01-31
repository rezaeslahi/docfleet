from typing import Any, Optional

from fastapi import APIRouter, Request

from clients.doc_client import get_document, list_documents

router = APIRouter(prefix="/documents", tags=["documents"])


@router.get("")
async def documents_list(request: Request,first_n:Optional[int] = None) -> Any:
    return await list_documents(request.state.request_id,first_n=first_n)


@router.get("/{doc_id}")
async def documents_get(doc_id: int, request: Request) -> Any:
    return await get_document(doc_id, request.state.request_id)

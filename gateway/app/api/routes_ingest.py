# from fastapi import APIRouter,Request
# from typing import Any,Dict,Optional
# from clients.downloader_client import download_docs
# from clients.doc_client import ingest_documents
# router = APIRouter(prefix="")


# @router.post("/ingest")
# async def ingest(request:Request,count:Optional[int] = None,include_text:Optional[bool]=True)->Dict[str,Any]:
#     request_id=request.state.request_id
#     res = await download_docs(request_id=request_id,count=count,include_text=include_text)
#     # TODO process the output 
#     documents_payload: Dict[str,Any] = {}
#     res2 = await ingest_documents(request_id=request_id,documents_payload=documents_payload)
#     # TODO process what should be returned
#     return {}

from fastapi import APIRouter, Request,HTTPException,status
from typing import Optional,Dict,Any,List
from app.clients.downloader_client import download_docs
from app.clients.doc_client import ingest_documents

router = APIRouter(prefix="")

@router.post("/download")
async def ingest(request:Request,count:Optional[int]=None)->Dict[str,Any]:
    request_id = request.state.request_id
    res = await download_docs(request_id=request_id,count=count)
    # shape of this res is {"count":int, "items":List[Dict]}
    items: List[Dict[str,Any]] = res.get("items",None)
    if items is None:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="Downloder has returned empty list")
    doc_list = [
        {"title":doc.get("title",""),
         "text":doc.get("text",""),
         "source_url":doc.get("url",""),
         "tags":["downloaded"]}
         for doc in items
    ]
    payload = {doc_list}
    ingested = await ingest_documents(request_id=request_id,documents_payload=payload)
    return {
        "downloaded": len(items),
        "ingested": len(ingested),
        "documents": [{"id": d["id"], 
        "title": d["title"]} for d in ingested],}
    pass
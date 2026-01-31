from httpx import Response, Timeout,AsyncClient
from typing import Optional,Dict,Any
from app.core.config import settings
from app.core.request_id import REQUEST_ID_HEADER
from fastapi import HTTPException,status
import asyncio
async def _request_to_downloader_service(
        method:str,
        url:str,
        request_id:str,
        json:Optional[Dict[str,Any]] = None,
        params:Optional[Dict[str,Any]] = None
)->Response:
    timeout = Timeout(settings.http_timeout_seconds)
    last_exc:Exception|None = None
    for itr in range(settings.http_retries):
        async with AsyncClient(timeout=timeout) as client:
            try:
                resp = await client.request(method=method,url=url,headers={REQUEST_ID_HEADER:request_id},json=json,params=params)
                return resp
            except(Exception) as e:
                if itr <settings.http_retries:
                    asyncio.sleep(0.1)
                    continue                
    raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY,detail=f"Downloader is no responding!{last_exc  }")

async def download_docs(request_id:str,count:Optional[int]=None,include_text:Optional[bool]=True)->Dict[str,Any]:
    method = "POST"
    url = f"{settings.downloader_service_url}/download"
    params ={}
    if count is not None:
        params["count":count]
    if include_text:
        params["include_text":include_text]
    resp = await _request_to_downloader_service(method=method,url=url,request_id=request_id,params=params)
    if resp.status_code != 200:
        raise HTTPException(status_code=resp.status_code,detail=resp.text)
    return resp.json()
    

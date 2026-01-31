import httpx
from fastapi import HTTPException,status
from typing import Optional, Dict, Any
from app.core.config import settings
from app.core.request_id import REQUEST_ID_HEADER
import asyncio



async def _request_to_user_service(
        method:str,
        url:str,
        request_id:str,
        json: Optional[Dict[str,Any]] = None,
        params: Optional[Dict[str,Any]]=None
)->httpx.Response:
    
    timeout = httpx.Timeout(settings.http_timeout_seconds)
    last_exc: Exception | None = None
    for itr in range(settings.http_retries):
        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                resp = await client.request(method=method,url=url,headers={REQUEST_ID_HEADER:request_id},json=json,params=params)
                return resp
        except(httpx.TimeoutException,httpx.TransportError) as e:
            
            if itr < settings.http_retries-1:
                asyncio.sleep(0.1)
                continue
    
    raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=f"user serice not responding: {last_exc}")

async def list_users(request_id:str,first_n:Optional[int] = None)-> Any:
    url = f"{settings.user_service_url}/users"
    params: Dict[str,Any] = {}
    if first_n is not None:
        params["first_n"]=first_n
    resp = await _request_to_user_service(method="GET", url=url,request_id=request_id,params=params)
    if resp.status_code != 200:
        raise HTTPException(status_code=resp.status_code,detail=resp.text)
    return resp.json()

async def get_user(user_id:int, request_id:str)->Any:
    url = f"{settings.user_service_url}/users/{user_id}"
    resp = await _request_to_user_service(method="GET",url=url,request_id=request_id)
    if resp.status_code != 200:
        raise HTTPException(status_code=resp.status_code, detail=resp.text)
    return resp.json()

async def create_user(request_id: str, payload: Dict[str,Any])->Any:
    url = f"{settings.user_service_url}/users"
    json = payload
    resp = await _request_to_user_service(method="POST",url=url,request_id=request_id,json=json)
    if resp.status_code != 201:
        raise HTTPException(status_code=resp.status_code,detail=resp.text)
    return resp.json()

async def update_user(request_id:str, user_id:int, paylod: Dict[str,Any])->Any:
    url = f"{settings.user_service_url}/users/{user_id}"
    json = paylod
    resp = await _request_to_user_service(method="PUT",url=url,request_id=request_id,json=json)
    if resp.status_code != 200:
        raise HTTPException(status_code=resp.status_code,detail=resp.text)
    return resp.json()
    
async def delete_user(request_id:str, user_id:int):
    url = f"{settings.user_service_url}/users/{user_id}"    
    resp = await _request_to_user_service(method="DELETE",url=url,request_id=request_id)
    if resp.status_code != 204:
        raise HTTPException(status_code=resp.status_code, detail=resp.text)

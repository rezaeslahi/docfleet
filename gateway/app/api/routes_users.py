from fastapi import APIRouter, Request, status
from typing import Optional,Any,Dict
from clients.user_client import list_users,get_user,delete_user,update_user,create_user

router = APIRouter(prefix="/users")

@router.get("")
async def user_list(request: Request, first_n:Optional[int] = None)->Any:
   return await list_users(first_n=first_n,request_id=request.state.request_id)

@router.get("/{user_id}")
async def user_get(request: Request, user_id:int)->Any:
   return await get_user(request_id=request.state.request_id,user_id=user_id)

@router.post("",status_code=status.HTTP_201_CREATED)
async def user_create(payload: Dict[str,Any],request:Request)->Any:
   return await create_user(request_id=request.state.request_id,payload=payload)

@router.put("/{user_id}")
async def user_update(payload:Dict[str,Any], user_id:int, request:Request)->Any:
   return await update_user(request_id=request.state.request_id,user_id=user_id,paylod=payload)

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def user_delete(user_id:int, request:Request)->None:
   await delete_user(request_id=request.state.request_id,user_id=user_id)
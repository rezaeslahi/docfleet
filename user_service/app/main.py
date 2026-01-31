from fastapi import FastAPI, HTTPException, status, Response
from typing import List, Optional
from .models import User,UserCreate,UserUpdate
from .store import user_store
from .core.logging import setup_logging
from .core.request_id import request_id_middleware
import logging
import uvicorn

setup_logging()
logger = logging.getLogger(__name__)

app = FastAPI(title="DocFleet User Service", version="0.1.0")
app.middleware("http")(request_id_middleware)


@app.get("/health")
async def health()->dict:
    return{"status":"ok"}

@app.get("/users",response_model=List[User])
async def get_users(first_n: Optional[int] = None)-> List[User]:
    return user_store.list_users(first_n)

@app.get("/users/{user_id}", response_model= User)
async def get_user(user_id:int)->User:
    user = user_store.get_user(user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.post("/users", response_model=User, status_code=status.HTTP_201_CREATED)
async def create_user(user_create: UserCreate)->User:
    user = user_store.user_create(user_create)
    return user

@app.put("/users/{user_id}", response_model=User, status_code=status.HTTP_200_OK)
async def update_user(user_id: int, user_update:UserUpdate)->User:
    user = user_store.update_user(user_id=user_id, user_update=user_update)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id:int)->Response:
    ok = user_store.delete_user(user_id=user_id)
    if not ok:
        raise HTTPException(status_code=404, detail="user not found")
    return Response(status_code=status.HTTP_204_NO_CONTENT)

def run_server():
    uvicorn.run(
        app="app.main:app",
        host="0.0.0.0",
        port= 8001,
        reload=True
    )
if __name__ == "__main__":
    run_server()


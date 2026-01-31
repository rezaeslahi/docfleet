from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from enum import Enum

class UserType(Enum):
    admin = "admin"
    designer = "designer"
    viewer = "viewer"

class UserModel(BaseModel):
    name: str = Field(...,min_length=2,max_length=100,description="This is user name")
    age: int = Field(...,ge=1,le=200,description="This is user age")
    email: EmailStr = Field(...,description="This is user email")
    user_type: UserType = Field(default=UserType.viewer, description= "This is user role")

class UserCreate(UserModel):
    pass

class UserUpdate(BaseModel):
    name: Optional[str] = Field(None,min_length=2,max_length=100,description="This is user name")
    age: Optional[int] = Field(None,ge=1,le=200,description="This is user age")
    email: Optional[EmailStr] = Field(None,description="This is user email")
    user_type: Optional[UserType] = Field(None, description= "This is user role")

class User(UserModel):
    id: int = Field(...,ge=1, description="This is user unique id") 

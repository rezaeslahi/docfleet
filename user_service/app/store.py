from typing import Dict, Optional, List
from .models import User, UserCreate, UserType, UserUpdate
from threading import Lock
from itertools import islice
class UserStore:
    
    # there should be a collection for users
    # there should be a lock
    # there should be an id generator
    # there should be functions for dealing with store
    global_id: int = 1
    def __init__(self):
        self._users: Dict[int,User] = {}
        self._lock = Lock()
        self._user_seed()
    
    def _user_seed(self):
        seed_users = [
            UserCreate(name="Reza", age=34, email="reza@example.com", user_type=UserType.admin),
            UserCreate(name="Leila", age=32, email="leila@example.com", user_type=UserType.designer),
            UserCreate(name="Rodin", age=3, email="rodin@example.com", user_type=UserType.viewer),
            UserCreate(name="Fatemeh", age=29, email="fatemeh@example.com", user_type=UserType.viewer),
            UserCreate(name="Soroosh", age=35, email="soroosh@example.com", user_type=UserType.designer),
        ]
        for u in seed_users:
            self.user_create(u)

    def user_create(self, user_create: UserCreate)->User:
        with self._lock:
            user = User(id=UserStore.global_id,name=user_create.name,age=user_create.age, email=user_create.email,user_type=user_create.user_type)
            self._users[UserStore.global_id] = user
            UserStore.global_id += 1
            return user
    
    def get_user(self, user_id:int)->User:
        return self._users[user_id]
    
    def list_users(self, first_n: Optional[int] = None)->List[User]:
        if first_n is None:
            return list(self._users.values())
        else:
            return list(islice(self._users.values(),first_n))
        
    def update_user(self,user_id: int, user_update:UserUpdate)->User | None:
        with self._lock:
            existing_user = self._users.get(user_id)
            if existing_user is None:
                return None
        
            if user_update.age is not None:
                existing_user.age = user_update.age
            if user_update.name is not None:
                existing_user.name = user_update.name
            if user_update.email is not None:
                existing_user.email = user_update.email
            if user_update.user_type is not None:
                existing_user.user_type = user_update.user_type
        
            return existing_user
    
    def delete_user(self, user_id:int)-> bool:
        with self._lock:
            user = self._users.pop(user_id,None)
            return user is not None
    
user_store = UserStore()
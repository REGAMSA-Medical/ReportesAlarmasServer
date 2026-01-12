from pydantic import BaseModel
from datetime import datetime

# READ
class UserReadSerializer(BaseModel):
    id:int
    firstname:str
    first_lastname:str
    second_lastname:str
    email = str
    password = str
    is_operator = bool 
    is_manager = bool
    is_supervisor = bool
    datetime = datetime

    class Config:
        from_attributes = True

# WRITE 
class UserCreateSerializer(BaseModel):
    firstname:str
    first_lastname:str
    second_lastname:str
    email:str
    password:str
    is_operator:bool
    is_manager:bool
    is_supervisor:bool
    
    class Config:
        from_attributes = True
        
class UserLoginSerializer(BaseModel):
    email:str
    password:str
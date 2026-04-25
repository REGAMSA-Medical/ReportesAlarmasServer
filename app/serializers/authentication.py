from pydantic import BaseModel, EmailStr
from datetime import datetime
from uuid import UUID

# READ
class UserReadSerializer(BaseModel):
    id:UUID
    firstname:str
    first_lastname:str
    second_lastname:str
    email:EmailStr
    role:str
    area_id:UUID
    area_name:str
    created_at:datetime
    updated_at:datetime
    
    class Config:
        from_attributes = True

# WRITE 
class UserCreateSerializer(BaseModel):
    firstname:str
    first_lastname:str
    second_lastname:str
    email:EmailStr
    password:str
    role:str
    area_id:UUID
    area_name:str
    
    class Config:
        from_attributes = True
        
class UserLoginSerializer(BaseModel):
    email:EmailStr
    password:str
from pydantic import BaseModel, EmailStr
from datetime import datetime

# READ
class UserReadSerializer(BaseModel):
    id:int
    firstname:str
    first_lastname:str
    second_lastname:str
    email:EmailStr
    password:str
    role:str = 'Jefe de Area'
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
    role:str='Jefe de Area'
    
    class Config:
        from_attributes = True
        
class UserLoginSerializer(BaseModel):
    email:EmailStr
    password:str
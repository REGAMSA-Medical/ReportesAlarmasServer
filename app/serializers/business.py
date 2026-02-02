from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class AreaReadSerializer(BaseModel):
    id:int
    name:str
    manager_id:int|None
    created_at:datetime
    updated_at:datetime
        
    class Config:
        from_attributes = True

class AreaManagerSerializer(BaseModel):
    id: int
    firstname: str
    first_lastname: str
    second_lastname: str
    role: str

    class Config:
        from_attributes = True

class AreaReadSerializer(BaseModel):
    id: int
    name: str
    manager_id: Optional[int]
    manager: Optional[AreaManagerSerializer] = None
    created_at: datetime
    
    class Config:
        from_attributes = True
from pydantic import BaseModel
from datetime import datetime
from uuid import UUID
from typing import Optional

class AreaReadSerializer(BaseModel):
    id: UUID
    name: str
    manager_id: Optional[UUID] = None
    created_at: datetime
    updated_at: datetime
        
    class Config:
        from_attributes = True

class AreaManagerSerializer(BaseModel):
    id: UUID
    firstname: str
    first_lastname: str
    second_lastname: str
    role: str

    class Config:
        from_attributes = True

class AreaReadSerializer(BaseModel):
    id: UUID
    name: str
    managed: bool
    created_at: datetime
    
    class Config:
        from_attributes = True
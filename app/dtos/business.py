from uuid import UUID
from pydantic import BaseModel

class AreaNameDTO(BaseModel):
    id: UUID
    name: str
    
    class Config:
        from_attributes = True

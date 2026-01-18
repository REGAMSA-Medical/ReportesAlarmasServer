from pydantic import BaseModel
from datetime import datetime

class AreaReadSerializer(BaseModel):
    id:int
    name:str
    manager_id:int|None
    created_at:datetime
    updated_at:datetime
        
    class Config:
        from_attributes = True
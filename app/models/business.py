from app.models.base import BaselineModel
from sqlalchemy import Column, String, Boolean

class Area(BaselineModel):
    __tablename__ = 'areas'
    name = Column(String, nullable=False, unique=True)
    managed = Column(Boolean, nullable=False, default=False)
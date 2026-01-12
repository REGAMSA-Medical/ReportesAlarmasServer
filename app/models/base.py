from app.database import Base
from sqlalchemy import Column, Integer, DateTime
from datetime import datetime

class BaselineModel(Base):
    __abstract__ = True
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=datetime.now, nullable=False)
    updated_at = Column(DateTime, onupdate=datetime.now, default=datetime.now, nullable=False)

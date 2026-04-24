from app.database import Base
from sqlalchemy import Column, DateTime
from datetime import datetime
from sqlalchemy.sql import func, text
from sqlalchemy.dialects.postgresql import UUID

class BaselineModel(Base):
    __abstract__ = True
    
    id = Column(UUID(as_uuid=True), primary_key=True, server_default=text("uuid_generate_v7()"), index=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, server_default=func.now(), nullable=False, index=True)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow,server_default=func.now(), server_onupdate=func.now(), nullable=False, index=True)
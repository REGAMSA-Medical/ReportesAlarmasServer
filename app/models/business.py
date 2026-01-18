from app.models.base import BaselineModel
from sqlalchemy import Column, String, ForeignKey, Integer
from sqlalchemy.orm import relationship

class Area(BaselineModel):
    __tablename__ = 'areas'
    name = Column(String, nullable=False, unique=True)
    manager_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    # 1:1 relation for the manager
    manager = relationship("User", foreign_keys=[manager_id], post_update=True)
    # 1:N relation for the employees
    employees = relationship("User", foreign_keys="[User.area_id]", back_populates="assigned_area")

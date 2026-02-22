from app.models.base import BaselineModel
from sqlalchemy import Column, String, ForeignKey, Integer

class User(BaselineModel):
    __tablename__ = 'users'

    firstname = Column(String, nullable=False, index=True)
    first_lastname = Column(String, nullable=False, index=True)
    second_lastname = Column(String, nullable=True, index=False)   
    email = Column(String, default=None, nullable=True, index=False)
    password = Column(String, nullable=False)
    role = Column(String, default='Jefe de Área', nullable=False, index=True)
    area_id = Column(Integer, ForeignKey('areas.id'), nullable=True)
    
from app.models.base import BaselineModel
from sqlalchemy import Column, String, Boolean
from sqlalchemy.orm import validates

class User(BaselineModel):
    __tablename__ = 'users'

    firstname = Column(String, nullable=False, index=True)
    first_lastname = Column(String, nullable=False, index=True)
    second_lastname = Column(String, nullable=True, index=False)   
    email = Column(String, default=None, nullable=True, index=False)
    role = Column(String, default='Jefe de Area', nullable=False, index=True)

    @validates('age')
    def validate_age(self, key, value):
        if value not in range(17, 80):
            raise ValueError('Inserta una edad valida (16 - 80 años)')
        return value
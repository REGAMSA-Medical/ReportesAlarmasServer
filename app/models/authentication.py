from app.models.base import BaselineModel
from sqlalchemy import Column, String, ForeignKey, Enum
from sqlalchemy.dialects.postgresql import UUID
from app.enums.authentication import UserRoleEnum

class User(BaselineModel):
    __tablename__ = 'users'

    firstname = Column(String, nullable=False)
    first_lastname = Column(String, nullable=False)
    second_lastname = Column(String)   
    email = Column(String, default=None)
    password = Column(String, nullable=False)
    role = Column(Enum(UserRoleEnum), default=UserRoleEnum.DIRECTIVE, nullable=False, index=True)
    area_id = Column(UUID(as_uuid=True), ForeignKey('areas.id', ondelete='SET NULL'))
    
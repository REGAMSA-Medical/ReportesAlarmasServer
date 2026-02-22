from app.models.base import BaselineModel
from sqlalchemy import Column, String, Float

class Product(BaselineModel):
    __tablename__ = 'products'

    model = Column(String, nullable=False, unique=True, index=True)
    code = Column(String, nullable=False, unique=True, index=True)
    cost = Column(Float, nullable=False)
    price = Column(Float, nullable=False)
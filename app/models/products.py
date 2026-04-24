from app.models.base import BaselineModel
from sqlalchemy import Column, String, Float, Enum
from app.enums.products import ProductTypeEnum

class Product(BaselineModel):
    __tablename__ = 'products'

    model = Column(String, nullable=False, unique=True)
    type = Column(Enum(ProductTypeEnum), default=ProductTypeEnum.ALARM, nullable=False, index=True)
    cost = Column(Float, nullable=False)
    price = Column(Float, nullable=False)
from app.models.base import BaselineModel
from sqlalchemy import Column, String, Boolean, Integer, ForeignKey, Enum
from app.enums.business import OrderStatusEnum

class Area(BaselineModel):
    __tablename__ = 'areas'
    
    name = Column(String, nullable=False, unique=True)
    managed = Column(Boolean, nullable=False, default=False)
    
class Stage(BaselineModel):
    __tablename__ = 'stages'
    
    name = Column(String, nullable=False, unique=True)
    
class Order(BaselineModel):
    __tablename__ = 'orders'
    
    customer_id = Column(Integer, ForeignKey('customers.id'), nullable=False)
    product_id = Column(Integer, ForeignKey('products.id'), nullable=False)
    stage = Column(Integer, ForeignKey('stages.id'), nullable=False, default=1, index=True)
    status = Column(Enum(OrderStatusEnum), nullable=False, default=OrderStatusEnum.NOT_STARTED, index=True)

class OrderStageEvidence(BaselineModel):
    __tablename__ = 'order_stage_evidence'
    
    order_id = Column(Integer, ForeignKey('orders.id'), nullable=False, index=True)
    stage_id = Column(Integer, ForeignKey('stages.id'), nullable=False, index=True)
    evidence_url = Column(String, nullable=False)
    description = Column(String, nullable=True)
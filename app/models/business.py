from app.models.base import BaselineModel
from sqlalchemy import Column, String, Boolean, Integer, ForeignKey, Enum

class OrderStatus(Enum):
    NOT_STARTED = "Not Started"
    IN_PROGRESS = "In Progress"
    COMPLETED = "Completed"
    CANCELED = "Canceled"

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
    status = Column(Enum(OrderStatus), nullable=False, default=OrderStatus.NOT_STARTED, index=True)
    
# I have to create table/model "OrderStageEvidence": order_id, stage, evidence(photo/image)
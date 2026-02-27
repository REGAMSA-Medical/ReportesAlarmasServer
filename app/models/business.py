from app.models.base import BaselineModel
from sqlalchemy import Column, String, Boolean, Integer, ForeignKey, Enum
from sqlalchemy.orm import relationship
from app.enums.business import OrderStatusEnum, AreaCategoryEnum

class Customer(BaselineModel):
    __tablename__ = 'customers'
    
    organization = Column(String, nullable=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=True)
    phone = Column(String, nullable=True)

class Area(BaselineModel):
    __tablename__ = 'areas'
    
    name = Column(String, nullable=False, unique=True)
    managed = Column(Boolean, nullable=False, default=False)
    """ Each Area independently of its name, must have a category. For example, there are 6 types of devices the enterprise produces,
    then, for every one of these devices, they have their engineering behind, despite they area different, they all are from an
    area that is of engineering type. So, this is applicable for administration, there are Human Resources and Customer Service,
    these both areas are of administration category"""
    category = Column(Enum(AreaCategoryEnum), nullable=False, default=AreaCategoryEnum.PRODUCTION, index=True) 
    
class Stage(BaselineModel):
    __tablename__ = 'stages'
    
    name = Column(String, nullable=False, unique=True)
    
class Order(BaselineModel):
    __tablename__ = 'orders'
    
    area_id = Column(Integer, ForeignKey('areas.id'), nullable=False)
    customer_id = Column(Integer, ForeignKey('customers.id'), nullable=False)
    product_id = Column(Integer, ForeignKey('products.id'), nullable=False)
    quantity = Column(Integer, nullable=False, default=1)
    stage_id = Column(Integer, ForeignKey('stages.id'), nullable=False, default=1, index=True)
    status = Column(Enum(OrderStatusEnum), nullable=False, default=OrderStatusEnum.NOT_STARTED, index=True)
    description = Column(String, nullable=True)
    # Joins
    stage = relationship("Stage")

class OrderStageEvidence(BaselineModel):
    __tablename__ = 'order_stage_evidence'
    
    order_id = Column(Integer, ForeignKey('orders.id'), nullable=False, index=True)
    stage_id = Column(Integer, ForeignKey('stages.id'), nullable=False, index=True)
    evidence_url = Column(String, nullable=False)
    description = Column(String, nullable=True)
    
class OrderHistoryTrack(BaselineModel):
    __tablename__ = 'order_history_track'
    
    order_id = Column(Integer, ForeignKey('orders.id'), nullable=False, index=True)
    stage_id = Column(Integer, ForeignKey('stages.id'), nullable=False)
    product_id = Column(Integer, ForeignKey('products.id'), nullable=False)
    area_id = Column(Integer, ForeignKey('areas.id'), nullable=False, index=True)
    status = Column(String, nullable=False) 
    notes = Column(String, nullable=True)
    # Joins
    order = relationship("Order")
    stage = relationship("Stage")
    product = relationship("Product")
    area = relationship("Area")
from app.models.base import BaselineModel
from sqlalchemy import Column, String, Boolean, Integer, ForeignKey, Enum, DateTime, Numeric
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.enums.business import OrderStatusEnum, OrderStageEnum
from datetime import datetime, timedelta

class Customer(BaselineModel):
    __tablename__ = 'customers'
    
    organization = Column(String)
    name = Column(String, nullable=False)
    email = Column(String)
    phone = Column(String, nullable=False)

class Area(BaselineModel):
    __tablename__ = 'areas'
    
    name = Column(String, nullable=False, unique=True)
    managed = Column(Boolean, nullable=False, default=False)
    
class Order(BaselineModel):
    __tablename__ = 'orders'
    
    customer_id = Column(UUID(as_uuid=True), ForeignKey('customers.id', ondelete='RESTRICT'), nullable=False, index=True)
    stage = Column(Enum(OrderStageEnum), default=OrderStageEnum.ORDER, nullable=False, index=True) # Current stage of the order
    status = Column(Enum(OrderStatusEnum), nullable=False, default=OrderStatusEnum.NOT_STARTED, index=True) # Completed, Not Started, In Progress, Canceled
    area_id = Column(UUID(as_uuid=True), ForeignKey('areas.id', ondelete='CASCADE'), nullable=False, index=True) # Current order area_id
    description = Column(String)
    due_date = Column(DateTime, default=lambda: datetime.today() + timedelta(weeks=1), nullable=False) 
    total_price = Column(Numeric(10, 2), default=0.0, nullable=False)
    
    # Joins
    customer = relationship("Customer", lazy="selectin")
    area = relationship("Area",  lazy="selectin")
    items = relationship("OrderItem", back_populates="order", lazy="selectin")
    history_tracks = relationship("OrderHistoryTrack", back_populates="order", lazy="selectin")

class OrderItem(BaselineModel):
    """
    Maneja cada item de la orden (haciendo referencia a la orden de la cual el item es parte, permitiendo tambien gestionar la cantidad de manera eficiente)
    """
    __tablename__ = 'order_items'
    
    order_id = Column(UUID(as_uuid=True), ForeignKey('orders.id', ondelete='CASCADE'), nullable=False)
    product_id = Column(UUID(as_uuid=True), ForeignKey('products.id', ondelete='CASCADE'), nullable=False)
    quantity = Column(Integer, nullable=False, default=1)
    # Joins
    order = relationship("Order", back_populates="items", lazy='selectin')
    product = relationship("Product", lazy='selectin')
    

class OrderStageEvidence(BaselineModel):
    """
    Order-Stage evidence is only saved when the order's process in the specific stage
    is completed, then, the manager can upload an image/a document as evidence.
    These are instances only for historic and evidence purposse.
    """
    
    __tablename__ = 'order_stage_evidence'
    
    order_id = Column(UUID(as_uuid=True), ForeignKey('orders.id', ondelete='CASCADE'), nullable=False, index=True)
    stage = Column(Enum(OrderStageEnum), default=OrderStageEnum.ORDER, nullable=False, index=True) 
    evidence_url = Column(String, nullable=False)
    description = Column(String)

class OrderHistoryTrack(BaselineModel):
    """
    Track every movement of the order in the workflow contemplating not only when its process in a stage is completed,
    but considering when is assigned, when is in progress, completed or even canceled.
    This is for historic track of movements in the workflow, and for presentations to directives.
    """
    
    __tablename__ = 'order_history_track'
    
    order_id = Column(UUID(as_uuid=True), ForeignKey('orders.id', ondelete='CASCADE'), nullable=False, index=True)
    product_id = Column(UUID(as_uuid=True), ForeignKey('products.id', ondelete='CASCADE'), nullable=False, index=True)
    area_id = Column(UUID(as_uuid=True), ForeignKey('areas.id', ondelete='CASCADE'), nullable=False, index=True)
    stage = Column(Enum(OrderStageEnum), default=OrderStageEnum.ORDER, nullable=False, index=True) 
    status = Column(Enum(OrderStatusEnum), default=OrderStatusEnum.NOT_STARTED, nullable=False) 
    # Joins
    order = relationship("Order", back_populates='history_tracks', lazy='selectin')
    product = relationship("Product", lazy='selectin')
    area = relationship("Area", lazy='selectin')
    
class Task(BaselineModel):
    """
    Tasks that are assigned from one area to another one. These tasks do not estrictly have to be related to the base
    product fabrication and delivery workflow, these can be tasks that are not contemplated, and only appear spontaneously.
    """
    __tablename__ = 'tasks'
    
    description =  Column(String, nullable=False) # Detalles de la tarea, descripción corta, instrucciones, etc
    reference_url = Column(String) # [Opcional]Referencia para la tarea a asignar (imagen, documento, archivo, etc.)
    from_area_id = Column(UUID(as_uuid=True), ForeignKey('areas.id', ondelete='CASCADE'), nullable=False, index=True) # Área que asigna la tarea
    to_area_id = Column(UUID(as_uuid=True), ForeignKey('areas.id', ondelete='CASCADE'), nullable=False, index=True) # Área a la cual se asigna la tarea
    due_date = Column(DateTime, default=datetime.today, nullable=False) # Fecha de entrega sugerida/estimada
    is_completed = Column(Boolean, default=False, nullable=False, index=True) # El primer paso es completar la tarea, aunqué no sea aceptada aún
    completed_at = Column(DateTime) # La fecha y hora en la cual fue completada la tarea
    is_acepted = Column(Boolean, default=False, nullable=False, index=True) # Es aceptada por el encargado de área que solicitó la tarea a otra área
    evidence_url = Column(String) # [Opcional] Evidencia de la tarea completada (imagen, documento, archivo, etc.)
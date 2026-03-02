from app.models.base import BaselineModel
from sqlalchemy import Column, String, Boolean, Integer, ForeignKey, Enum
from sqlalchemy.orm import relationship
from app.enums.business import OrderStatusEnum, AreaCategoryEnum, OrderStageEnum

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
    then, for every one of these devices, they have their engineering behind, despite their area is different, they all are from an
    area that is of engineering type. So, this is applicable for administration, there are Human Resources and Customer Service,
    these both areas are of administration category"""
    category = Column(Enum(AreaCategoryEnum), nullable=False, default=AreaCategoryEnum.PRODUCTION, index=True) 
    
class Stage(BaselineModel):
    __tablename__ = 'stages'
    
    """
    - Pedido: El cliente realiza el pedido
    - Administración: Se evalua disponibilidad de materiales, personal y tiempo, y negociación con cliente
    - Ingenieria: Se genera orden de trabajo a ingenieria
    - Producción: Se produce y ensambla el dispositivo/producto
    - Testing: Se realizan pruebas y control de calidad
    - Embalaje: Se empaca el producto para su envio
    - Envio: Se lleva a centros de envio y paqueteria
    - Cliente: El cliente recibe el producto
    """
    name = Column(Enum(OrderStageEnum), nullable=False, unique=True, index=True)
    
class Order(BaselineModel):
    __tablename__ = 'orders'
    
    customer_id = Column(Integer, ForeignKey('customers.id'), nullable=False)
    product_id = Column(Integer, ForeignKey('products.id'), nullable=False)
    quantity = Column(Integer, nullable=False, default=1)
    stage_id = Column(Integer, ForeignKey('stages.id'), nullable=False, default=1, index=True) # To Kno in which stage the order is at the moment
    status = Column(Enum(OrderStatusEnum), nullable=False, default=OrderStatusEnum.NOT_STARTED, index=True) # Completed, Not Started, In Progress, Canceled
    current_area_id = Column(Integer, ForeignKey('areas.id'), nullable=False, index=True)
    description = Column(String, nullable=True)
    # Joins
    stage = relationship("Stage")

class OrderStageEvidence(BaselineModel):
    """
    Order-Stage evidence is only saved when the order's process in the specific stage
    is completed, then, the manager can upload an image as evidence.
    These are instances only for historic and evidence purposse.
    """
    
    __tablename__ = 'order_stage_evidence'
    
    order_id = Column(Integer, ForeignKey('orders.id'), nullable=False, index=True)
    stage_id = Column(Integer, ForeignKey('stages.id'), nullable=False, index=True)
    evidence_url = Column(String, nullable=False)
    description = Column(String, nullable=True)

class AreaStageProductConfig(BaselineModel):
    """
    Defines the visibility and responsibility matrix for different enterprise areas.

    This model acts as a master filter to restrict which orders a department manager 
    can monitor or manage based on their area's specialized scope. For example, 
    the 'Brazos' area manager should only be authorized to view orders currently 
    in 'Ingeniería' or 'Producción' stages, and specifically for 'Brazos' type products.

    area_id: Reference to the specific department (Brazos, Compresores).
    stage_id: Reference to the authorized workflow stage (Producción, Ingeniería, Administración).
    product_id: Optional reference to a specific product model. If null, the area has visibility over all products within that stage.
    """
    __tablename__ = 'area_stage_product_config'
    
    area_id = Column(Integer, ForeignKey('areas.id'), nullable=False)
    stage_id = Column(Integer, ForeignKey('stages.id'), nullable=False)
    product_id = Column(Integer, ForeignKey('products.id'), nullable=True) # Si es null, aplica a todos los productos de esa área
    
    area = relationship("Area")
    stage = relationship("Stage")
    product = relationship("Product")
    
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
"""
Enums of base business data that must be a rule
that new business model incoming data must follow
"""

import enum

class OrderStatusEnum(enum.Enum):
    NOT_STARTED = "Nuevo"
    IN_PROGRESS = "Comenzado"
    COMPLETED = "Completado"
    CANCELED = "Cancelado"
    
class OrderStageEnum(enum.Enum):
    """
    An order participates in different stages, and that order has 4 posible statuses by stage.
    """
    ORDER = 'Pedido'
    PRODUCTION = 'Producción'
    BOARDING = 'Embarque'
    
class AreaEnum(enum.Enum):
    """
    Every area participates in a different order stage, except for direction area, 
    direction only cares about info, metrics, workflow visualization and historic data.
    """
    DIRECTION = 'Dirección'
    SELLS = 'Ventas'
    ALARMS = 'Alarmas'
    DELIVERY = 'Enbarque'
import enum

"""
Enums of base business data that must be a rule
that new business model incoming data must follow
"""

class OrderStatusEnum(enum.Enum):
    NOT_STARTED = "Not Started"
    IN_PROGRESS = "In Progress"
    COMPLETED = "Completed"
    CANCELED = "Canceled"
    
class OrderStageEnum(enum.Enum):
    ORDER = 'Order'
    ADMINISTRATION = 'Administration'
    ENGINEERING = 'Engineering'
    PRODUCTION = 'Production'
    TESTING = 'Testing'
    PACKAGING = 'Packaging'
    DELIVERY = 'Delivery'
    RECEIVEMENT = 'Receivement'
    
class AreaCategoryEnum(enum.Enum):
    ADMINISTRATION = 'Administration'
    ENGINEERING = 'Engineering'
    PRODUCTION = 'Production'
    LOGISTICS = 'Logistics'
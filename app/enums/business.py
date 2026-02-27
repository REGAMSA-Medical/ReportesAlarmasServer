import enum

class OrderStatusEnum(enum.Enum):
    NOT_STARTED = "Not Started"
    IN_PROGRESS = "In Progress"
    COMPLETED = "Completed"
    CANCELED = "Canceled"
    
class AreaCategoryEnum(enum.Enum):
    ADMINISTRATION = 'Administration'
    ENGINEERING = 'Engineering'
    PRODUCTION = 'Production'
    LOGISTICS = 'Logistics'
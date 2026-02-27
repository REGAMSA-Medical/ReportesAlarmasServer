from app.models.base import BaselineModel
from sqlalchemy import Column, String, ForeignKey, Integer

class OrderReport(BaselineModel):
    """
    Report instances area created right after an order is delivered to the client
    and the entire lifecycle is finished, just as evidence and history of what is done
    """
    __tablename__ = 'order_report'
    
    order_id = Column(Integer, ForeignKey('orders.id'), nullable=False, index=True)
    location_url = Column(String, nullable=False)
    
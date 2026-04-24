from app.models.base import BaselineModel
from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID

class OrderReport(BaselineModel):
    """
    Report instances area created right after an order is delivered to the client
    and the entire lifecycle is finished, just as evidence and history of what is done
    """
    __tablename__ = 'order_report'
    
    order_id = Column(UUID(as_uuid=True), ForeignKey('orders.id', ondelete='CASCADE'), nullable=False, index=True)
    location_url = Column(String, nullable=False)
    
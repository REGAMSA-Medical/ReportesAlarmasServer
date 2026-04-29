from fastapi import APIRouter, Depends
from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models.business import Order
from app.decorators.common import handle_http_exceptions
from app.enums.business import OrderStageEnum, OrderStatusEnum, AreaEnum

router = APIRouter(prefix='/orders', tags=['Orders'])

@router.post('/createOrder')
@handle_http_exceptions
async def create_order(request:Request, db:AsyncSession = Depends(get_db)):
    """
    Create an order from scratch, obtaining the data from request.forn.
    Include a selected customer from an existing list, the stage is ORDER by default,
    the status is IN_PROGRESS by default (because its created but not assigned (COMPLETED) to production yet),
    the area_id can be any production area, but ALARMS by default,
    the description is optional, and free.
    """
    pass
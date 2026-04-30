from fastapi import APIRouter, Depends
from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models.business import Order, Area
from app.decorators.common import handle_http_exceptions
from app.enums.business import OrderStageEnum, OrderStatusEnum, AreaEnum
from app.utils.logger import logger
from sqlalchemy import select
from app.utils.responses import NotCreatedItemErrorResponse

router = APIRouter(prefix='/orders', tags=['Orders'])

@router.post('/createOrder')
@handle_http_exceptions
async def create_order(request:Request, db:AsyncSession = Depends(get_db)):
    """
    Create an order from scratch, obtaining the data from request.forn.
    Include a selected customer from an existing list, the stage is ORDER by default,
    the status is IN_PROGRESS by default (because its created but not assigned (COMPLETED) to production yet),
    the area_id is set as default by the id of SELLS area,
    the description is optional, and free.
    """
    # Request form data 
    data = await request.form()
    logger.info('Obtained form data')
    
    # Obtain SELLS area id
    area_id = db.execute(select(Area.id).where(Area.name == AreaEnum.SELLS.name))
    logger.info('Obtained SELLS area id')
    
    try: 
        # Create order
        new_order = Order(
            customer_id=data.get('customer_id'),
            stage = OrderStageEnum.ORDER,
            status = OrderStatusEnum.IN_PROGRESS,
            area_id = area_id,
            description=data.get('description')|'Hay una nueva orden',
        )
        
        db.add(new_order)
        await db.commit()
        await db.refresh(new_order)
        logger.info(f"Created new order [{new_order}]")
    except Exception as e:
        return NotCreatedItemErrorResponse(error=e)
    
    return {'item':new_order}
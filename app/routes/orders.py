from fastapi import APIRouter, Depends
from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models.business import Order, OrderItem, Area
from app.decorators.common import handle_http_exceptions
from app.enums.business import OrderStageEnum, OrderStatusEnum, AreaEnum
from app.utils.logger import logger
from sqlalchemy import select
from app.utils.responses import NotCreatedItemErrorResponse
import json

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
    body = await request.body()    
    data = json.loads(body)
    logger.info('Obtained body data')
    
    # Obtain SELLS area id
    area_id = db.execute(select(Area.id).where(Area.name == AreaEnum.SELLS.name))
    logger.info('Obtained SELLS area id')
    
    # Calculate total order price
    total_price = 0
    
    for item in data['order_items']:
        total_price+=(item.quantity*item.price)
    
    try: 
        # Create order
        new_order = Order(
            customer_id=data['customer_id'],
            stage = OrderStageEnum.ORDER,
            status = OrderStatusEnum.IN_PROGRESS,
            area_id = area_id,
            description=data['description'],
            total_price=total_price
        )
        
        db.add(new_order)
        await db.commit()
        await db.refresh(new_order)
        logger.info(f"Created new order {new_order}")
    except Exception as e:
        return NotCreatedItemErrorResponse(error=e)
    
    # Transactional: Rollback and commit are automatic
    async with db.begin():

        order_items = data["items"]

        for item in order_items:
            new_item = OrderItem(
                order_id=new_order.id,
                product_id=item.product_id,
                quantity=item.quantity,
            )
                        
            db.add(new_item)
            
    logger.info(f"Added items to the new order {new_order.id}")
    
    return {'item':new_order}
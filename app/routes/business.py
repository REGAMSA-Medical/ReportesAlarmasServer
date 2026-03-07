from fastapi import APIRouter, Depends
from fastapi.exceptions import HTTPException
from app.database import get_db
from sqlalchemy import select
from app.models.business import Area, Order, OrderHistoryTrack, Stage, AreaStageProductConfig
from app.models.products import Product
from app.serializers.business import AreaReadSerializer
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.utils.logger import logger
from app.enums.business import OrderStatusEnum
from datetime import timedelta, timezone

router = APIRouter(prefix='/business', tags=['Business'])

@router.get('/areas/list')
async def get_areas(db: AsyncSession = Depends(get_db)):
    try:
        query = select(Area).where(Area.managed==False, Area.name!='Dirección')
        result = await db.execute(query)
        areas_from_db = result.scalars().all()
    
        if not areas_from_db:
            raise HTTPException(status_code=404, detail='No se encontraron áreas disponibles')

        areas = [AreaReadSerializer.from_orm(area) for area in areas_from_db]
        
        return {'items': areas}
        
    except Exception as e:
        logger.error(f"Areas List Error: {str(e)}")
        raise HTTPException(status_code=500, detail=f'Unexpected Error: {e}')
    
    
@router.get('/recentActivityByUserArea')
async def get_recent_activity_by_user_area(id: int, db: AsyncSession = Depends(get_db)):
    try:
        config_query = select(AreaStageProductConfig).where(AreaStageProductConfig.area_id == id)
        config_result = await db.execute(config_query)
        allowed_configs = config_result.scalars().all()

        if not allowed_configs:
            return HTTPException(status_code=404)

        allowed_stages = [c.stage_id for c in allowed_configs]
        allowed_products = [c.product_id for c in allowed_configs if c.product_id is not None]
        from datetime import datetime

        query = (
            select(
                OrderHistoryTrack.id,
                Product.model,
                OrderHistoryTrack.status,
                Stage.name.label("stage_name"),
                OrderHistoryTrack.created_at.label("date")
            )
            .join(Product, OrderHistoryTrack.product_id == Product.id)
            .join(Stage, OrderHistoryTrack.stage_id == Stage.id)
            .where(OrderHistoryTrack.area_id == id)
            .where(OrderHistoryTrack.stage_id.in_(allowed_stages))
            .where(OrderHistoryTrack.created_at >= datetime.now(timezone.utc) - timedelta(weeks=2))
        )

        if allowed_products:
            query = query.where(OrderHistoryTrack.product_id.in_(allowed_products))

        query = query.order_by(OrderHistoryTrack.created_at.desc())
        
        result = await db.execute(query)
        
        history_data = [
            {
                "id": row.id,
                "model": row.model,
                "status": row.status,
                "stage": row.stage_name,
                "date": row.date
            } 
            for row in result.all()
        ]
        
        return {"items": history_data}

    except Exception as e:
        logger.error(f"Unexpected Error in Recent Activity: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")  
    
@router.get('/ordersOverallInfoByUserArea')
async def get_orders_overall_info_by_user_area(id: int, db: AsyncSession = Depends(get_db)):
    try:
        async def get_orders_by_status(status: OrderStatusEnum):
            query = (
                select(Order)
                .join(Stage, Order.stage_id == Stage.id)
                .where(Order.status == status, Order.current_area_id == id)
            )
            result = await db.execute(query)
            return result.scalars().all()

        return {
            "items": {
                'new': await get_orders_by_status(OrderStatusEnum.NOT_STARTED),
                'process': await get_orders_by_status(OrderStatusEnum.IN_PROGRESS),
                'completed': await get_orders_by_status(OrderStatusEnum.COMPLETED),
            }
        }
    except Exception as e:
        logger.error(f'Unexpected Error: {str(e)}')
        raise HTTPException(status_code=500, detail="Error interno del servidor")
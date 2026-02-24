from fastapi import APIRouter, Depends
from fastapi.exceptions import HTTPException
from app.database import get_db
from sqlalchemy import select
from app.models.business import Area, Order, OrderHistoryTrack, Stage
from app.models.products import Product
from app.serializers.business import AreaReadSerializer
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.utils.logger import logger

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
async def get_recent_activity_by_user_area(id:int, db: AsyncSession = Depends(get_db)):
    try:
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
            .order_by(OrderHistoryTrack.created_at.desc())
        )
        
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
        logger.error(f"Unexpected Error: {e}")
        raise HTTPException(status_code=500, detail=f'Unexpected Error: {e}')
    
    
@router.get('/ordersOverallInfoByUserArea')
async def get_orders_overall_info_by_user_area(id: int, db: AsyncSession = Depends(get_db)):
    try:
        async def get_orders_by_stage(stage_name: str):
            query = (
                select(Order)
                .join(Stage, Order.stage_id == Stage.id)
                .where(Stage.name == stage_name, Order.area_id == id)
            )
            result = await db.execute(query)
            return result.scalars().all()

        return {
            "items": {
                'under_review': await get_orders_by_stage('Under Review'),
                'to_do': await get_orders_by_stage('To Do'),
                'production': await get_orders_by_stage('Production'),
                'testing': await get_orders_by_stage('Testing'),
                'shipping': await get_orders_by_stage('Shipping'),
                'delivery': await get_orders_by_stage('Delivery'),
            }
        }
    except Exception as e:
        logger.error(f'Unexpected Error: {str(e)}')
        raise HTTPException(status_code=500, detail="Error interno del servidor")
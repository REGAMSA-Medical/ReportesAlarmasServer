from fastapi import APIRouter, Depends
from fastapi.exceptions import HTTPException
from app.database import get_db
from sqlalchemy import select
from app.models.business import Area, Order
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
    
@router.get('/ordersOverallInfoByUserArea')
async def get_orders_overall_info_by_user_area(id, db: AsyncSession = Depends(get_db)):
    try:
        # Under review 
        query = select(Order).where(Order.stage=='Under Review', Order.area_id==id)
        result = await db.execute(query)
        under_review = result.scalars().all()
        
        # To do
        query = select(Order).where(Order.stage=='To Do', Order.area_id==id)
        result = await db.execute(query)
        to_do = result.scalars().all()
        
        # Production
        query = select(Order).where(Order.stage=='Production', Order.area_id==id)
        result = await db.execute(query)
        production = result.scalars().all()
        
        # Quality assurance
        query = select(Order).where(Order.stage=='Testing', Order.area_id==id)
        result = await db.execute(query)
        testing = result.scalars().all()
        
        # Shipping
        query = select(Order).where(Order.stage=='Shipping', Order.area_id==id)
        result = await db.execute(query)
        shipping = result.scalars().all()
        
        # Delivery
        query = select(Order).where(Order.stage=='Delivery', Order.area_id==id)
        result = await db.execute(query)
        delivery = result.scalars().all()
        
        return {
                'item': {
                    'to_do':to_do,
                    'production':production,
                    'testing':testing,
                    'shipping':shipping,
                    'delivery':delivery,
                    'under_review':under_review
                }
            }
    except Exception as e:
        logger.error(f'Unexpected Error: {str(e)}')
        raise HTTPException(status_code=500, detail=f'Unexpected Error: {e}')
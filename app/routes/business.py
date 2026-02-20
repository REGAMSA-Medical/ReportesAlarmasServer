from fastapi import APIRouter, Depends
from fastapi.exceptions import HTTPException
from app.database import get_db
from sqlalchemy import select
from app.models.business import Area
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
        raise HTTPException(status_code=500, detail=f'Areas List Error: {e}')
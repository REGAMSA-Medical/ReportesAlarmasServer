from fastapi import APIRouter, Depends, Response
from fastapi.exceptions import HTTPException
from app.database import get_db
from sqlalchemy import select
from app.models.business import Area
from app.serializers.business import AreaReadSerializer
from sqlalchemy.orm import joinedload 
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix='/business', tags=['Business'])

@router.get('/areas/list')
async def get_areas(db: AsyncSession = Depends(get_db)):
    try:
        query = select(Area).options(joinedload(Area.manager))
        result = await db.execute(query)
        areas_db = result.scalars().all()
    
        if not areas_db:
            raise HTTPException(status_code=404, detail='No se encontraron áreas registradas')

        areas_serialized = [AreaReadSerializer.from_orm(area) for area in areas_db]
        
        return {'items': areas_serialized}
        
    except Exception as e:
        print(f"DEBUG ERROR: {str(e)}")
        raise HTTPException(status_code=500, detail='Error interno al obtener áreas')
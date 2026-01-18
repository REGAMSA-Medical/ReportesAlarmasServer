from fastapi import APIRouter, Depends, Response
from fastapi.exceptions import HTTPException
from app.database import get_db
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models.business import Area
from app.serializers.business import AreaReadSerializer

router = APIRouter(prefix='/business', tags=['Business'])

@router.get('/areas')
async def get_areas(db: Session = Depends(get_db)):
    try:
        result = await db.execute(select(Area))
        areas = result.scalars().all()
    
        if not areas:
            raise HTTPException(status_code=404, detail='No se encontraron areas registradas')

        areas = [AreaReadSerializer.from_orm(area) for area in areas]
        
        return {'items': areas}
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f'Error del servidor: {str(e)}')

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.business import Area 
from app.utils.logger import logger

AREAS_LIST = [
    'Dirección', 'Alarmas', 'Brazos', 'Torno', 'RRHH', 
    'Ventas', 'Consolas', 'Compresores', 'Laser', 'Almacen'
]

async def insertAreasPipeline(db: AsyncSession):
    """
    Inserta las áreas base si no existen en la base de datos.
    """
    try:
        # Obtain areas that already exist
        result = await db.execute(select(Area.name))
        existing_areas = {row[0] for row in result.all()}
        
        areas_to_insert = []
        
        # Filter areas that do not exist yet
        for name in AREAS_LIST:
            if name not in existing_areas:
                areas_to_insert.append(Area(name=name, managed=False))
                
        if not areas_to_insert:
            logger.info('There are no new areas to insert')
            return

        # Add all new areas
        db.add_all(areas_to_insert)
        await db.commit()
        
        logger.info(f'Inserted new areas: {len(areas_to_insert)}.')

    except Exception as e:
        await db.rollback() # Revert in case of error
        logger.error(f'Areas Insert Error: {str(e)}')
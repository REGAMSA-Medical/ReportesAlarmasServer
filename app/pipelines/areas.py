from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.business import Area 
from app.utils.logger import logger
from app.enums.business import AREAS_LIST

"""
Pipelines for insertion at db level
of initial & base, business necesary data
"""

async def insertAreasPipeline(db: AsyncSession):
    """
    Insert base areas in db if they don't exist.
    """
    try:
        # Obtain areas that already exist
        result = await db.execute(select(Area.name))
        existing_areas = {row[0] for row in result.all()}
        
        areas_to_insert = []
        
        # Filter areas that do not exist yet
        for name, category in AREAS_LIST:
            if name not in existing_areas:
                areas_to_insert.append(Area(name=name, category=category, managed=False))
                
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
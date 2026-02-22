from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.business import Stage 
from app.utils.logger import logger

STAGES_LIST = ['Under Review', 'To Do', 'Production', 'Testing', 'Shipping', 'Delivery']

async def insertStagesPipeline(db: AsyncSession):
    """
    Inserta las áreas base si no existen en la base de datos.
    """
    try:
        # Obtain stages that already exist
        result = await db.execute(select(Stage.name))
        existing_areas = {row[0] for row in result.all()}
        
        stages_to_insert = []
        
        # Filter stages that do not exist yet
        for name in STAGES_LIST:
            if name not in existing_areas:
                stages_to_insert.append(Stage(name=name))
                
        if not stages_to_insert:
            logger.info('There are no new stages to insert')
            return

        # Add all new stages
        db.add_all(stages_to_insert)
        await db.commit()
        
        logger.info(f'Inserted new stages: {len(stages_to_insert)}.')

    except Exception as e:
        await db.rollback() # Revert in case of error
        logger.error(f'Stages Insert Error: {str(e)}')
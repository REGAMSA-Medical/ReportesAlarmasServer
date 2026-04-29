from fastapi import APIRouter, Depends
from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
from app.database import get_db
from app.models.business import Task
from app.utils.logger import logger
from app.utils.files import upload_media_file
from app.decorators.common import handle_http_exceptions

router = APIRouter(prefix='/tasks', tags=['Tasks'])

# TASKS
@router.post('/assignTask')
@handle_http_exceptions
async def assign_task( request: Request, db: AsyncSession = Depends(get_db)):
    """
    Assign a task from one area to another area.
    The assigned task can be any type of task that can be done by another area.
    The assigned task is an emergent task, that means, it is now alligned directly with the standart  manufacturing workflow,
    If a file is uploaded, that file is stored in the local server in media/ directory (switching to AWS S3 in a near future).
    """

    # Request form data 
    request_data = await request.form()
    
    # Handle file upload if provided
    file_data = request_data.get('file')
    
    if file_data:
        # Save file to media
        await upload_media_file(file_data) 
    
    new_task = Task(
        description=request_data.get('description'),
        reference_url=request_data.get('reference_url'),
        from_area_id=request_data.get('from_area_id'),
        to_area_id=request_data.get('to_area_id'),
        due_date=datetime.strptime(request_data.get('due_date'), '%Y-%m-%d %H:%M:%S'),
        is_completed=False,
        completed_at=None,
        is_acepted=False,
        evidence_url=None
    )
    
    db.add(new_task)
    await db.commit()
    await db.refresh(new_task)
    logger.info(f"Task assigned successfully [{new_task.id}]")
    
    return {'item':new_task}
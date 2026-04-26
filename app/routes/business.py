from fastapi import APIRouter, Depends
from fastapi.exceptions import HTTPException
from fastapi import UploadFile, Request
from app.database import get_db
from sqlalchemy import select
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta, timezone
from app.models.business import Area, Order, OrderHistoryTrack, Task, OrderStageEvidence
from app.models.products import Product
from app.models.authentication import User
from app.serializers.business import AreaReadSerializer
from app.utils.logger import logger
from app.enums.business import OrderStatusEnum, OrderStageEnum
import shutil
from pathlib import Path
from app.decorators.common import handle_http_exceptions

router = APIRouter(prefix='/business', tags=['Business'])

# AREAS
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
    
@router.get('/areas/list/simplified')
async def get_areas_simplified(area_id: int, db: AsyncSession = Depends(get_db)):
    try:
        query = (
            select(
                Area.id.label("area_id"), 
                Area.name.label("area_name"), 
                User.firstname.label("area_manager_firstname"),
                User.first_lastname.label("area_manager_lastname")
            )
            .join(User, Area.id == User.area_id)
            .where(
                Area.managed == True, 
                Area.name != 'Dirección',
                Area.id != area_id
            )
        )
        
        result = await db.execute(query)
        
        areas_from_db = result.mappings().all()
    
        if not areas_from_db:
            raise HTTPException(status_code=404, detail='No se encontraron áreas disponibles')

       # Format manually (Serializers do not work here because the query did not returned complete objects)
        areas = [
            {
                "area_id": row["area_id"],
                "area_name": row["area_name"],
                "area_manager_name": f'{row["area_manager_firstname"]} {row["area_manager_lastname"]}'
            } 
            for row in areas_from_db
        ]
        
        return {'items': areas}
    except Exception as e:
        logger.error(f"Areas List Error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
    
    
# ORDERS
@router.get('/recentActivityByUserArea')
async def get_recent_activity_by_user_area(id: str, db: AsyncSession = Depends(get_db)):
    """
    Get recent activity by user area (new assigned tasks, moment when a task is started, a task is completed, cancelled tasks, etc)
    Only area managers can access to this info directly.
    This retrieves the order track id, product model, order status, order stage and datetime when this event was registered.
    """
    try:
        query = (
            select(
                OrderHistoryTrack.id,
                Product.model,
                OrderHistoryTrack.status,
                OrderHistoryTrack.stage,
                OrderHistoryTrack.created_at.label("date")
            )
            .join(Product, OrderHistoryTrack.product_id == Product.id)
            .where(OrderHistoryTrack.area_id == id)
            .where(OrderHistoryTrack.created_at >= datetime.now(timezone.utc) - timedelta(weeks=1))
            .order_by(OrderHistoryTrack.created_at.desc())
        )
        
        result = await db.execute(query)
        rows = result.scalars().all()

        if not rows:
            return HTTPException(status_code=404, detail='There are no recent activity for this area')

        history_data = [
            {
                "id": row.id,
                "model": row.model,
                "status": row.status,
                "stage": row.stage_name,
                "date": row.date
            } 
            for row in rows
        ]
        
        return {"items": history_data}

    except Exception as e:
        logger.error(f'Unexpected Error: {e}')
        raise HTTPException(status_code=500, detail=f'Unexpected Error: {e}')  
    
@router.get('/ordersOverallInfoByUserArea')
async def get_orders_overall_info_by_user_area(id: int, db: AsyncSession = Depends(get_db)):
    """
    Get all orders asigned to an area categorized by their status (new/not started, in progress, completed).
    Every one of this categorized orders include all fields from its Order model.
    """
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

@handle_http_exceptions
@router.get('/orders/list/byArea')
async def get_orders_list_by_user_area(id: int, db: AsyncSession =  Depends(get_db)):
    """
    Get list of all orders corresponding to an area, fetching them by user area id.
    """
    
    query = (
        select(Order.id, Order.product, Order.customer)
        .where(Order.current_area_id == id)
    )
        
    result = await db.execute(query)
    
    return result.scalars().all()


async def save_file(file: UploadFile) -> str:
    """
    Save uploaded file to the media directory organized by file type.
    This function accepts an uploaded file, determines its type based on MIME type,
    saves it to the appropriate subdirectory (images, audios, documents, videos, other),
    and returns the relative file path.
    """
    # Define media directory path (project root level)
    media_dir = Path("media")
    
    # Create media directory if it doesn't exist
    media_dir.mkdir(exist_ok=True)
    
    # Determine file type based on MIME type
    mime_type = file.content_type or ""
    
    if mime_type.startswith("image/"):
        subdir = "images"
    elif mime_type.startswith("audio/"):
        subdir = "audios"
    elif mime_type.startswith("video/"):
        subdir = "videos"
    elif mime_type in ["application/pdf", "application/msword", "application/vnd.openxmlformats-officedocument.wordprocessingml.document", 
                       "application/vnd.ms-excel", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", 
                       "text/plain", "application/json"]:
        subdir = "documents"
    else:
        subdir = "other"
    
    # Create subdirectory if it doesn't exist
    subdir_path = media_dir / subdir
    subdir_path.mkdir(exist_ok=True)
    
    # Generate unique filename to avoid collisions
    import uuid
    from datetime import datetime
    
    # Get file extension
    file_extension = Path(file.filename).suffix if file.filename else ""
    
    # Create unique filename: timestamp_uuid.extension
    unique_filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}{file_extension}"
    
    # Define full file path
    file_path = subdir_path / unique_filename
    
    try:
        # Save the file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Return relative path from project root
        return str(file_path)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")
    
    
# TASKS
@router.post('/tasks')
async def create_task( request: Request, db: AsyncSession = Depends(get_db)):
    try:
        # Get request form data 
        request_data = await request.form()
        
        # Handle file upload if provided
        file_data = request_data.get('file')
        
        if file_data:
            # Save file to media
            await save_file(file_data) 
        
        new_task = Task(
            description=request_data.get('description'),
            reference_url=request_data.get('reference_url'),
            from_area_id=int(request_data.get('from_area_id')),
            to_area_id=int(request_data.get('to_area_id')),
            due_date=datetime.strptime(request_data.get('due_date'), '%Y-%m-%d %H:%M:%S'),
            is_completed=False,
            completed_at=None,
            is_acepted=False,
            evidence_url=None
        )
        
        db.add(new_task)
        await db.commit()
        await db.refresh(new_task)
        logger.info(f"Task created successfully [{new_task.id}]")
        
        return {'item':new_task}
        
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f'Server Error: {str(e)}', exc_info=True)
        raise HTTPException(status_code=500, detail=f'Server Error: {str(e)}')
    
# EVIDENCES
@router.post('/evidences')
async def upload_evidence(request: Request, db: AsyncSession = Depends(get_db)):
    """
    - Area manager upload an evidence, in photo or document when their task is already finished.
    - Evidence is saved for report generation.
    - Once the evidence is uploaded the order/product is moved to the next step in the workflow.
    - Notify the next area in the next stage that the order is moved to their area to continue the workflow, as a not_started order.
    - Order's data for report is retrieved in case the area manager wants to generate a report.
    """
    
    try:
         # Get request form data 
        request_data = await request.form()
        
        product_id = request_data.get('product_id')
        area_id = request_data.get('request_user_area_id')
        order_id = request_data.get('order_id')
        stage_id = request_data.get('stage_id')
        evidence_url = request_data.get('evidence_url')
        description = f'La orden {request_data.get("order_id")} completó la etapa de {request_data.get("stage_id")}'
        
        # Handle file upload if provided
        file_data = request_data.get('file')
        
        if file_data:
            # Save file to media (Switch to S3 in a near future)
            await save_file(file_data) 
        
        # Save evidence in DB
        new_evidence = OrderStageEvidence(
            order_id=order_id,
            stage_id=stage_id,
            evidence_url=evidence_url,
            description=description
        )
        
        db.add(new_evidence)
        await db.commit()
        await db.refresh(new_evidence)
        logger.info(f"Evidence uploaded successfully [{new_evidence.id}]")
        
        # Save completed process in OrderHistoryTrack
        completed_order_history_track = OrderHistoryTrack(
            order_id=order_id,
            stage_id=stage_id,
            product_id=product_id,
            area_id=area_id,
            status=OrderStatusEnum.COMPLETED,
            notes=f'Proceso finalizado en el area de {area_id} para la orden {order_id}'
        )
        
        db.add(completed_order_history_track)
        await db.commit()
        await db.refresh(completed_order_history_track)
        
        # Move order to the next stage
        stage_name = f'SELECT name FROM stages WHERE id={request_data.get('stage_id')}'
        
        stages_list = ['Order', 'Administration', 'Engineering', 'Production', 'Testing', 'Packaging', 'Delivery', 'Receivement']
        
        if stage_name in stages_list:
            next_index = stages_list.index(stage_name)+1
            stage_name = stages_list[next_index]
            
        next_stage_id = f'SELECT id FROM stages WHERE name={stage_name}'
        
        next_area_id = f'SELECT area_id FROM area_stage_product_config WHERE stage_id={next_stage_id} AND product_id={product_id}'
        
        # Save new process for the next area in the workflow in OrderHistoryTrack
        assigned_order_history_track = OrderHistoryTrack(
            order_id=order_id,
            stage_id=next_stage_id,
            product_id=product_id,
            area_id=next_area_id,
            status=OrderStatusEnum.NOT_STARTED,
            notes=f'La orden {order_id} ha sido asignada al area de {next_area_id}'
        )
        
        db.add(assigned_order_history_track)
        await db.commit()
        await db.refresh(assigned_order_history_track)
        
        # Save order in a new stage in db
        new_order_stage = f'UPDATE orders SET stage_id={stage_id}, status={OrderStatusEnum.NOT_STARTED} WHERE id={request_data.get('order_id')}'
        
        # Notify next area manager enroled in the next stage
        pass
        
        # Return success response
        return {'item':new_evidence}
        
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f'Server Error: {str(e)}', ext_info=True)
        raise HTTPException(status_code=500, detail=f'Server Error: {str(e)}')
    
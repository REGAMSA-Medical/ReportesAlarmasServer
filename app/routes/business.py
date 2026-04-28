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
from app.dtos.business import AreaNameDTO
from app.utils.logger import logger
from app.enums.business import OrderStatusEnum
import shutil
from pathlib import Path
from app.decorators.common import handle_http_exceptions, handle_exceptions
from app.utils.responses import NotFoundItemsResponse

router = APIRouter(prefix='/business', tags=['Business'])

@router.get('/areas')
@handle_http_exceptions
async def get_areas(managed : None | bool  = None, db : AsyncSession = Depends(get_db)):
    """
    Get list of areas with all their fields.
    Can bt filtered by 'managed' == True or 'managed' == False, or None by default to return all. 
    """
    
    query = select(Area)
    
    if managed in [True, False]:
        query = query.where(Area.managed == managed)
    
    result = await db.execute(query)
    areas = result.scalars().all()
    
    if not areas:
        return NotFoundItemsResponse()
    
    return {
        'items':areas
    }

# AREAS
@router.get('/areasNames')
@handle_http_exceptions
async def get_areas_names(include_managed_areas: bool = True, include_direction_area: bool = True, db: AsyncSession = Depends(get_db)):
    """
    Get the list of areas' names, areas that are not managed by an area manager.
    Id field is included as index for frontend implementations.
    Dirección area is excluded.
    """
    query = (
        select(Area.id, Area.name)
    )
    
    if include_managed_areas == False:
        query = query.where(Area.managed==False) 
    
    if include_direction_area == False:
        query = query.where(Area.name!='Dirección')
        
    result = await db.execute(query)
    areas = result.mappings().all()

    if not areas:
        return NotFoundItemsResponse()

    areas = [AreaNameDTO.from_orm(area) for area in areas]
    
    return {'items': areas}
   
@router.get('/areasSimplified')
@handle_http_exceptions
async def get_areas_simplified(area_id: str, include_user_area: bool, db: AsyncSession = Depends(get_db)):
    """
    Obtain a list of areas in a simplified format with not all fields.
    The user area is only included in the list when 'include_user_area' is True.
    The response is a list of objects(areas), each with area_id, area_name, area_manager_name.
    """
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
            (Area.id != area_id if (include_user_area == True) else None)
        )
    )

    result = await db.execute(query)
    
    areas_from_db = result.mappings().all()

    if not areas_from_db:
        return NotFoundItemsResponse()

    areas = [
        {
            "area_id": row["area_id"],
            "area_name": row["area_name"],
            "area_manager_name": f'{row["area_manager_firstname"]} {row["area_manager_lastname"]}'
        } 
        for row in areas_from_db
    ]
    
    return {'items': areas}
    
# ORDERS
@router.get('/recentActivityByUserArea')
@handle_http_exceptions
async def get_recent_activity_by_user_area(id: str, db: AsyncSession = Depends(get_db)):
    """
    Get recent activity by user area (new assigned tasks, moment when a task is started, a task is completed, cancelled tasks, etc)
    Only area managers can access to this info directly.
    This retrieves the order track id, product model, order status, order stage and datetime when this event was registered.
    """
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
        return NotFoundItemsResponse()

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
    
@router.get('/ordersOverallInfoByUserArea')
@handle_http_exceptions
async def get_orders_overall_info_by_user_area(id: str, db: AsyncSession = Depends(get_db)):
    """
    Get all orders asigned to an area categorized by their status (new/not started, in progress, completed).
    Every one of this categorized orders include all fields from its Order model.
    """
    async def get_orders_by_status(status: OrderStatusEnum):
        query = (
            select(Order)
            .where(Order.status == status, Order.area_id == id)
        )
        result = await db.execute(query)
        return result.scalars().all()

    items = {
        'new': await get_orders_by_status(OrderStatusEnum.NOT_STARTED),
        'process': await get_orders_by_status(OrderStatusEnum.IN_PROGRESS),
        'completed': await get_orders_by_status(OrderStatusEnum.COMPLETED),
    }

    empty_keys = 0
    for key, value in items.items():
        if len(value) == 0:
            empty_keys+=1
        
    if empty_keys > 0:    
        return NotFoundItemsResponse()

    return {
        "items": items
    }

@router.get('/ordersByArea')
@handle_http_exceptions
async def get_orders_by_area(area_id: str | None = None, db: AsyncSession =  Depends(get_db)):
    """
    Get list of all orders corresponding to an area, fetching them by user area id or obtaining all of them.
    """
    
    query = (select(Order.id, Order.product, Order.customer).where(Order.current_area_id == id)) if (area_id) else (select(Order.id, Order.product, Order.customer))
        
    result = await db.execute(query)
    orders = result.scalars().all()
    
    if not orders:
        return NotFoundItemsResponse()
        
    return {
        'items':orders
    }
    
    
# TASKS
@router.post('/assignTask')
@handle_http_exceptions
async def assign_task( request: Request, db: AsyncSession = Depends(get_db)):

    # Request form data 
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


# EVIDENCES
@router.post('/uploadEvidence')
@handle_http_exceptions
async def upload_evidence(request: Request, db: AsyncSession = Depends(get_db)):
    """
    - Area manager upload an evidence, in photo or document when their task is already finished.
    - Evidence is saved for report generation.
    - Once the evidence is uploaded the order/product is moved to the next step in the workflow.
    - Notify the next area in the next stage that the order is moved to their area to continue the workflow, as a not_started order.
    - Order's data for report is retrieved in case the area manager wants to generate a report.
    """
    # Request form data 
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
        
from fastapi import APIRouter, Depends
from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.decorators.common import handle_http_exceptions

router = APIRouter(prefix='/orders', tags=['Orders'])

@router.post('/createOrder')
@handle_http_exceptions
async def create_order(request:Request, db:AsyncSession = Depends(get_db)):
    pass
from fastapi import APIRouter
from fastapi.responses import JSONResponse

router = APIRouter(prefix='/authentication', tags=['Authentication'])

@router.get('/userInfo')
async def userInfo() -> JSONResponse:
    return JSONResponse(content={'item':{
        'id':1,
        'username':'Emanuel',
        'role':'Mecatronics Engineer'
    }}, status_code=200)
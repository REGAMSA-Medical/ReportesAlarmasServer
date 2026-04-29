from fastapi import APIRouter, Depends
from fastapi.exceptions import HTTPException
from app.database import get_db
from app.serializers.authentication import UserCreateSerializer, UserLoginSerializer
from app.models.authentication import User
from app.models.business import Area
from app.utils.authentication import create_tokens, hash_password, verify_password, JWT_SECRET_KEY, ALGORITHM
from jose import jwt
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.utils.logger import logger
from app.decorators.common import handle_http_exceptions

router = APIRouter(prefix='/auth', tags=['Authentication'])

@router.post('/signUp')
@handle_http_exceptions
async def signUp(data: UserCreateSerializer, db: AsyncSession = Depends(get_db)):
    logger.info(f"Iniciando registro para email: {data.email}")
    
    ROLE_MAPPING = {
        'Dirección General': 'DIRECTIVE',
        'Jefe de Área': 'AREA_MANAGER'
    }

    data.role = ROLE_MAPPING.get(data.role, data.role)
    
    # Verify existing email
    result = await db.execute(select(User).filter(User.email == data.email))
    if result.scalars().first():
        logger.warning(f"Intento de registro con email duplicado: {data.email}")
        raise HTTPException(status_code=400, detail='El email ya está registrado')

    # Verify area exists
    area_res = await db.execute(select(Area).filter(Area.id == data.area_id))
    area = area_res.scalar_one_or_none()
    
    if not area:
        logger.error(f"Área con ID {data.area_id} no encontrada")
        raise HTTPException(status_code=404, detail="El área seleccionada no existe")

    # Verify already managed area
    if data.role == "AREA_MANAGER":
        if area.managed:
            logger.warning(f"Intento de asignar segundo Jefe al área: {area.name}")
            raise HTTPException(
                status_code=400, 
                detail=f"El área '{area.name}' ya tiene un Jefe asignado."
            )
        area.managed = True
        logger.info(f"Área '{area.name}' marcada como gestionada.")

    # Avoid same person in the same rol and department/area
    same_area_query = select(User).filter(
        func.upper(func.trim(User.firstname)) == func.upper(func.trim(data.firstname)),
        func.upper(func.trim(User.first_lastname)) == func.upper(func.trim(data.first_lastname)),
        User.role == data.role,
        User.area_id == data.area_id
    )
    
    if data.second_lastname and data.second_lastname.strip():
        same_area_query = same_area_query.filter(
            func.upper(func.trim(User.second_lastname)) == func.upper(func.trim(data.second_lastname))
        )

    res_duplicate = await db.execute(same_area_query)
    if res_duplicate.scalars().first():
        logger.warning(f"Ya existe un {data.role} con ese nombre en esta área.")
        raise HTTPException(
            status_code=400,
            detail=f"Ya existe un {data.role} con ese nombre en esta área."
        )
    
    # Create user
    hashed_pwd = hash_password(data.password)

    new_user = User(
        firstname=data.firstname, 
        first_lastname=data.first_lastname, 
        second_lastname=data.second_lastname, 
        email=data.email, 
        password=hashed_pwd,
        role=data.role, 
        area_id=data.area_id
    )
    
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    logger.info(f"Usuario {new_user.id} creado exitosamente y guardado en DB")
    
    # Obtain user, and area_name with a join
    final_query = (
        select(User, Area.name)
        .join(Area, User.area_id == Area.id)
        .filter(User.id == new_user.id)
    )
    final_res = await db.execute(final_query)
    user_row, area_name = final_res.first()

    access_token, refresh_token = create_tokens({'sub': user_row.email})
    logger.info(f"Tokens JWT generados para {user_row.email}. Proceso finalizado.")
    
    return {
        'access_token': access_token,
        'refresh_token': refresh_token,
        'token_type': 'bearer',
        'user': {
            'id': user_row.id,
            'email': user_row.email,
            'firstname': user_row.firstname,
            'first_lastname': user_row.first_lastname,
            'second_lastname': user_row.second_lastname,
            'role': user_row.role,
            'area_id': user_row.area_id,
            'area_name': area_name
        }
    }

@router.post('/signIn')
@handle_http_exceptions
async def signIn(credentials: UserLoginSerializer, db: AsyncSession = Depends(get_db)):
    user_area = (
        select(User, Area.name)
        .join(Area, User.area_id == Area.id)
        .filter(User.email == credentials.email)
    )
    area_res  = await db.execute(user_area)
    user, area_name = area_res.first()
    
    if not user:
        raise HTTPException(status_code=404, detail='El usuario no existe')
        
    if not verify_password(credentials.password, user.password):
        raise HTTPException(status_code=401, detail='Credenciales incorrectas')
    
    access_token, refresh_token = create_tokens({'sub': user.email})
    
    return {
        'access_token': access_token,
        'refresh_token': refresh_token,
        'token_type': 'bearer',
        'user': {
            'id': user.id,
            'email': user.email,
            'firstname': user.firstname,
            'first_lastname': user.first_lastname,
            'second_lastname': user.second_lastname,
            'role': user.role,
            'area_id': user.area_id,
            'area_name': area_name
        }
    }

from pydantic import BaseModel

class RefreshTokenRequest(BaseModel):
    refresh_token: str

@router.post('/refreshJWT')
@handle_http_exceptions
async def refreshJWT(request: RefreshTokenRequest):
    payload = jwt.decode(request.refresh_token, JWT_SECRET_KEY, algorithms=[ALGORITHM])
    
    # Validate that token is of refresh type
    if payload.get('type') != 'refresh':
        raise HTTPException(status_code=401, detail='Token inválido')
        
    email: str = payload.get('sub')
    if email is None:
        raise HTTPException(status_code=401, detail='Token inválido')
        
    # Generate a new tokens pair
    new_access, new_refresh = create_tokens({'sub': email})
    return {'access_token': new_access, 'refresh_token': new_refresh}
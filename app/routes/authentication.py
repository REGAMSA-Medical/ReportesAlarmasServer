from fastapi import APIRouter, Depends
from fastapi.exceptions import HTTPException
from fastapi.responses import JSONResponse
from app.database import get_db
from app.serializers.authentication import UserCreateSerializer, UserLoginSerializer
from app.models.authentication import User
from app.utils.authentication import create_tokens, hash_password, verify_password, JWT_SECRET_KEY, ALGORITHM
from jose import JWTError
import jwt
from sqlalchemy.orm import Session

router = APIRouter(prefix='/auth', tags=['Authentication'])

@router.get('/userInfo')
async def userInfo() -> JSONResponse:
    return JSONResponse(content={'item':{
        'id':1,
        'username':'Emanuel',
        'role':'Mecatronics Engineer'
    }}, status_code=200)

@router.post('/signUp')
async def signUp(user_data: UserCreateSerializer, db: Session = Depends(get_db)):
    try:
        # Verify if user already exists
        existing_user = db.query(User).filter(User.email == user_data.email).first()
        if existing_user:
            raise HTTPException(status_code=400, detail='El email ya está registrado')
        
        # Hash password and save it on db for the new created user
        hashed_pwd = hash_password(user_data.password)
        new_user = User(email=user_data.email, hashed_password=hashed_pwd)
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        # Generate tokens for direct access after sign In
        access_token, refresh_token = create_tokens({'sub': new_user.email})
        
        return {
            'access_token': access_token,
            'refresh_token': refresh_token,
            'token_type': 'bearer',
            'user':new_user
        }
    except Exception as e:
        return HTTPException(status_code=500, detail=f'Error inesperado: {e}')
    
@router.post('/signIn')
async def signIn(credentials: UserLoginSerializer, db: Session = Depends(get_db)):
    try:
        user = db.query(User).filter(User.email == credentials.email).first()
        
        if not user or not verify_password(credentials.password, user.hashed_password):
            raise HTTPException(status_code=401, detail='Credenciales incorrectas')
        
        access_token, refresh_token = create_tokens({'sub': user.email})
        
        return {
            'access_token': access_token,
            'refresh_token': refresh_token,
            'token_type': 'bearer',
            'user':user
        }
    except Exception as e:
        return HTTPException(status_code=500, detail=f'Error inesperado: {e}')

@router.post('/refreshJWT')
async def refreshJWT(refresh_token: str):
    try:
        payload = jwt.decode(refresh_token, JWT_SECRET_KEY, algorithms=[ALGORITHM])
        
        # Validate that token is of refresh type
        if payload.get('type') != 'refresh':
            raise HTTPException(status_code=401, detail='Token inválido')
            
        email: str = payload.get('sub')
        if email is None:
            raise HTTPException(status_code=401, detail='Token inválido')
            
        # Generate a new tokens pair
        new_access, new_refresh = create_tokens({'sub': email})
        return {'access_token': new_access, 'refresh_token': new_refresh}
        
    except JWTError:
        raise HTTPException(status_code=401, detail='Token expirado o inválido')
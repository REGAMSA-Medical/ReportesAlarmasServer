from fastapi import APIRouter, Depends
from fastapi.exceptions import HTTPException
from fastapi.responses import JSONResponse
from app.database import get_db
from app.serializers.authentication import UserCreateSerializer, UserLoginSerializer
from app.models.authentication import User
from app.utils.authentication import create_tokens, hash_password, verify_password, JWT_SECRET_KEY, ALGORITHM
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from sqlalchemy import select

router = APIRouter(prefix='/auth', tags=['Authentication'])

@router.post('/signUp')
async def signUp(user_data: UserCreateSerializer, db: Session = Depends(get_db)):
    try:
        # Verify if user already exists
        result = await db.execute(select(User).filter(User.email == user_data.email))
        existing_user = result.scalars().first()
        
        if existing_user:
            raise HTTPException(status_code=400, detail='El email ya está registrado')
        
        # Hash password  
        hashed_pwd = hash_password(user_data.password)
        
        # Save new user
        new_user = User(firstname=user_data.firstname, first_lastname=user_data.first_lastname, second_lastname=user_data.second_lastname, email=user_data.email, role=user_data.role, password=hashed_pwd)
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
        raise HTTPException(status_code=500, detail=f'Error inesperado: {e}')
    
@router.post('/signIn')
async def signIn(credentials: UserLoginSerializer, db: Session = Depends(get_db)):
    try:
        result = await db.execute(select(User).filter(User.email == credentials.email))
        user = result.scalars().first()
        
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
                'role': user.role
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'Error inesperado: {str(e)}')

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
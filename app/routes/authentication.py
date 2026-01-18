from fastapi import APIRouter, Depends
from fastapi.exceptions import HTTPException
from app.database import get_db
from app.serializers.authentication import UserCreateSerializer, UserLoginSerializer
from app.models.authentication import User
from app.utils.authentication import create_tokens, hash_password, verify_password, JWT_SECRET_KEY, ALGORITHM
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from sqlalchemy import select, func

router = APIRouter(prefix='/auth', tags=['Authentication'])

@router.post('/signUp')
async def signUp(user_data: UserCreateSerializer, db: Session = Depends(get_db)):
    try:
        print("=" * 50)
        print("[LOG] DEBUG SIGNUP INICIADO")
        print(f"[LOG] Email recibido: {user_data.email}")
        
        # Verify if user already exists
        result = await db.execute(select(User).filter(User.email == user_data.email))
        existing_user = result.scalars().first()
        
        print(f"[LOG] Usuario ya existe?: {existing_user is not None}")
        
        if existing_user:
            print("[LOG] Usuario ya registrado")
            raise HTTPException(status_code=400, detail='El email ya está registrado')
        
        if user_data.role == "Jefe de Área":
            # Verify if there is an area boss asigned to that area
            area_boss_query = select(User).filter(
                User.role == "Jefe de Área",
                User.area == user_data.area
            )
            result = await db.execute(area_boss_query)
            existing_boss = result.scalars().first()

            if existing_boss:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Ya existe un Jefe de Área asignado a '{user_data.area}'. "
                           f"Solo se permite un responsable por departamento."
                )
        
        same_area_query = select(User).filter(
            func.upper(func.trim(User.firstname)) == func.upper(func.trim(user_data.firstname)),
            func.upper(func.trim(User.first_lastname)) == func.upper(func.trim(user_data.first_lastname)),
            func.upper(func.trim(User.role)) == func.upper(func.trim(user_data.role))
        )

        # Lastnames validation
        if user_data.second_lastname and user_data.second_lastname.strip():
            same_area_query = same_area_query.filter(
                func.upper(func.trim(User.second_lastname)) == func.upper(func.trim(user_data.second_lastname))
            )

        result = await db.execute(same_area_query)
        existing_same_area = result.scalars().first()

        if existing_same_area:
            raise HTTPException(
                status_code=400,
                detail=f'Ya existe un {user_data.role} con el nombre {user_data.firstname} {user_data.first_lastname}. '
                    f'Por favor, verifica que no sea la misma persona o contacta al administrador.'
            )
        
        # Hash password  
        hashed_pwd = hash_password(user_data.password)
        print(f"[LOG] Hash generado (primeros 30 chars): {hashed_pwd[:30]}...")
        
        # Save new user
        new_user = User(
            firstname=user_data.firstname, 
            first_lastname=user_data.first_lastname, 
            second_lastname=user_data.second_lastname, 
            email=user_data.email, 
            role=user_data.role, 
            area=user_data.area,
            password=hashed_pwd
        )
        print(f"[LOG] Objeto User creado en memoria")
        
        db.add(new_user)
        print("[LOG] Usuario agregado a la sesión")
        
        await db.commit()
        print("[LOG] Commit realizado")
        
        await db.refresh(new_user)
        print(f"[LOG] Usuario refrescado. ID: {new_user.id}")
        print(f"[LOG] Email en objeto: {new_user.email}")
        
        # Verify user was saved
        verification = await db.execute(select(User).filter(User.id == new_user.id))
        verified_user = verification.scalars().first()
        print(f"[LOG] Verificación en BD: {'EXISTE' if verified_user else 'NO EXISTE'}")
        
        # Generate tokens
        access_token, refresh_token = create_tokens({'sub': new_user.email})
        print("[LOG] Tokens generados")
        print("=" * 50)
        
        return {
            'access_token': access_token,
            'refresh_token': refresh_token,
            'token_type': 'bearer',
            'user': {
                'id': new_user.id,
                'email': new_user.email,
                'firstname': new_user.firstname,
                'first_lastname': new_user.first_lastname,
                'second_lastname': new_user.second_lastname,
                'role': new_user.role,
                'area': new_user.area
            }
        }
    except Exception as e:
        print(f"[ERROR] ERROR EN SIGNUP: {str(e)}")
        print(f"[ERROR] TIPO DE ERROR: {type(e)}")
        import traceback
        traceback.print_exc()
        print("=" * 50)
        raise HTTPException(status_code=500, detail=f'Error del servidor: {str(e)}')
    
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
                'role': user.role,
                'area': user.area
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
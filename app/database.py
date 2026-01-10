from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase
from dotenv import load_dotenv
from typing import Annotated
from fastapi import Depends
import os
from dotenv import load_dotenv

load_dotenv()

# DB: URL de la base de datos asincrona para operaciones CRUD
OPERATOR_DB_URL = os.getenv('OPERATOR_DB_URL') 

# DB: Motor de base de datos asincrono para operaciones CRUD
async_engine = create_async_engine(OPERATOR_DB_URL)
async_session = async_sessionmaker(bind=async_engine, autocommit=False)

class Base(DeclarativeBase):
    pass

# DB: Metodos y Funciones
async def get_db():
    """
    Obtiene la instancia de la base de datos para ejecutar sus funciones, como realizar consultas.
    Se utiliza ampliamente en toda la aplicación como dependencia.
    Nos permite acceder a un objeto de tipo base de datos sin necesidad de instanciarlo mas de 1 vez a nivel aplicación. 
    Requiere usar el patrón de Inyección de Dependencias (DI) con el módulo FastAPI.Depends.
    
    Retorna:
    - database:Database: Instancia de la base de datos asíncrona PostgreSQL.
    """
    async with async_session() as session:
        yield session

async def end_db():
    """
    Cierra la base de datos.
    """
    await async_engine.dispose()
    print("DB close")

# Dependencia directa de la base de datos
db_dependency = Annotated[AsyncSession, Depends(get_db)]
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from . database import end_db
from . utils.logger import logger
# Import routers
from app.routes.authentication import router as authRouter
from app.routes.business import router as businessRouter

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    try:
        logger.info('Init API')
    except Exception as e:
        print(f'API Init Error: {e}')
    yield
    # Shutdown
    await end_db()
    logger.info('Closed API')

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get('/')
async def root() -> JSONResponse:
    return JSONResponse(content={'message':'Bienvenido a la API de REGAMSA Medical'}, status_code=200)

app.include_router(authRouter)
app.include_router(businessRouter)
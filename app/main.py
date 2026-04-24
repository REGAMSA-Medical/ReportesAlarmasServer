# Dependencies
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from redis import Redis
# App 
from . database import end_db, get_db
from . utils.logger import logger
from . pipelines.areas import insertAreasPipeline
# Import routers
from app.routes.authentication import router as authRouter
from app.routes.business import router as businessRouter

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    try:
        # Redis 
        app.state.redis = Redis(host='localhost', port=6379)
        
        # Database
        logger.info('Run Server')
        async_session_generator = get_db()
        
        # Seed data
        db = await anext(async_session_generator)
        await insertAreasPipeline(db)
        
    except Exception as e:
        logger.error(f'Server Startup Error: {e}')
    yield
    # Shutdown
    app.state.redis.close()
    logger.info('Shutdown Redis')
    await end_db()
    logger.info('Shutdown Server')

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
    return JSONResponse(content={'message':'Regamsa Medical API'}, status_code=200)

app.include_router(authRouter)
app.include_router(businessRouter)
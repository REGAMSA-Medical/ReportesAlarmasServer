from fastapi import FastAPI
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from . database import end_db

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    try:
        print('Init API')
    except Exception as e:
        print(f'API Init Error: {e}')
    yield
    # Shutdown
    await end_db()
    print('API close')

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

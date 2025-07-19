import uvicorn
import logging

from dotenv import load_dotenv
from fastapi import FastAPI, Response, Request
from contextlib import asynccontextmanager

from controllers.firebase import register_user_firebase, login_user_firebase
from controllers.cancionescatalogo import get_cancion_catalogo, get_canciones_by_genre, create_cancion

from models.Userregister import UserRegister
from models.Userlogin import UserLogin
from models.cancionescatalogo import CancionCatalogo

from utils.security import validateadmin
from utils.telemetry import setup_simple_telemetry, instrument_fastapi_app

logging.basicConfig( level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
load_dotenv()

telemetry_enabled = setup_simple_telemetry()

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting API...")
    yield
    logger.info("Shutting down API...")

app = FastAPI( title="API-canciones",
    description="canciones API Lab expert system",
    version="0.5.0",
    lifespan=lifespan
    )

if telemetry_enabled:
    from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
    FastAPIInstrumentor.instrument_app(app)
    logger.info("Application Insights telemetry is enabled")
else:
    logger.warning("Application Insights telemetry is not enabled, check your .env file")

@app.get("/api/health")
async def health_check():
    return {"status": "ok",
            "version": "0.5.0"
            }

###Get###

@app.get("/api/version")
def get_version():
    return {"version": "0.5.0"}

@app.get("/")
def read_root():
    return {"message": "Bienvenido a mi API con FastAPI"}

@app.get("/api/canciones/catalogo", response_model=list[CancionCatalogo])
async def get_canciones_catalogo() -> list[CancionCatalogo]:
    
    canciones: list[CancionCatalogo] = await get_cancion_catalogo()
    return canciones

@app.get("/api/canciones/catalogo/", response_model=list[CancionCatalogo])
async def get_canciones_catalogo_by_genre(track_genre: str) -> list[CancionCatalogo]:
    canciones: list[CancionCatalogo] = await get_canciones_by_genre(track_genre)
    return canciones

@app.get("/test/validate")
@validateadmin
async def validate_admin(request: Request, response: Response):
    
    return {"message": "Validación de administrador exitosa"}


###Post###

@app.post("/api/users/register")
async def register(user: UserRegister):
    return await register_user_firebase(user)

@app.post("/api/users/login")
async def login(user: UserLogin):
    return await login_user_firebase(user)    

@app.post("/api/canciones")
@validateadmin
async def create_cancion_api(request: Request, response: Response,cancion: CancionCatalogo) -> CancionCatalogo:
    return await create_cancion(cancion)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
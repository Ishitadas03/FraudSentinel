import logging
import sys
from contextlib import asynccontextmanager
from pathlib import Path

# Ensure backend and project root are in sys.path
_BACKEND_DIR = Path(__file__).resolve().parent.parent
_PROJECT_ROOT = _BACKEND_DIR.parent
for _p in [str(_BACKEND_DIR), str(_PROJECT_ROOT)]:
    if _p not in sys.path:
        sys.path.insert(0, _p)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.core.database import Base, SessionLocal, engine
from app.models import AuditLog, Customer, Forecast, FraudAlert, Investigation, ModelPrediction, Role, Transaction, User
from app.schemas.health import HealthResponse, RootResponse

logger = logging.getLogger("fraudsentinel")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: initialize database tables and seed baseline admin/analyst/viewer users if needed."""
    try:
        # Create tables if not present
        Base.metadata.create_all(bind=engine)
        db = SessionLocal()
        try:
            from scripts.seed import seed_roles, seed_default_users
            roles = seed_roles(db)
            seed_default_users(db, roles)
            db.commit()
        except Exception as e:
            db.rollback()
            logger.warning("Startup seeding check notice: %s", e)
        finally:
            db.close()
    except Exception as err:
        logger.warning("Database startup init notice: %s", err)
    yield


app = FastAPI(
    title="FraudSentinel API",
    description="Fraud Detection, Risk Analysis & Forecasting System API",
    version="1.0.0",
    lifespan=lifespan,
)

# Enable CORS for local development with frontend applications & Vercel deployments
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "*",
    ],
    allow_origin_regex=r"^https:\/\/.*\.vercel\.app$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include modular API router under /api/v1
app.include_router(api_router, prefix="/api/v1")


@app.get("/", response_model=RootResponse, tags=["System"])
def read_root():
    return {
        "message": "FraudSentinel API",
        "version": "1.0.0",
        "status": "running",
    }


@app.get("/api", response_model=RootResponse, tags=["System"], include_in_schema=False)
def read_api_root():
    return {
        "message": "FraudSentinel API",
        "version": "1.0.0",
        "status": "running",
    }


@app.get("/health", response_model=HealthResponse, tags=["System"])
def health_check():
    return {
        "status": "healthy",
    }


@app.get("/api/health", response_model=HealthResponse, tags=["System"], include_in_schema=False)
def health_check_api_alias():
    return {
        "status": "healthy",
    }

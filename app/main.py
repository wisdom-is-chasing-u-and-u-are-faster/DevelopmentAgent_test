"""
Sustainable Clothing Marketplace - Carbon Footprint Engine Service
FastAPI Entrypoint and Application Lifecycle
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import init_db
from app.api.v1.endpoints import carbon, health


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize database tables and seed emission factors on startup
    init_db()
    yield


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description=(
        "Microservice for product and shipping carbon calculation, "
        "LCA accounting, Patch offsets, and immutable ledger."
    ),
    lifespan=lifespan
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount API Routers
app.include_router(health.router, tags=["Health"])
app.include_router(carbon.router, prefix=f"{settings.API_V1_STR}/carbon", tags=["Carbon Footprint Engine"])

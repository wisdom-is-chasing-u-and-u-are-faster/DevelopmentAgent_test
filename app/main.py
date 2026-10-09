"""
Main Application Entrypoint for ETMS
Mounts all REST microservice routers, static asset directories, and lifecycle handlers.
"""

import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.db.init_db import init_database
from app.api.tickets import router as tickets_router
from app.api.routing import router as routing_router
from app.api.sla import router as sla_router
from app.api.audit import router as audit_router
from app.api.notifications import router as notifications_router
from app.api.search import router as search_router
from app.api.settings import router as settings_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize DB schema and baseline seeds upon startup
    init_database()
    yield


app = FastAPI(
    title="Enterprise Ticketing Management System (ETMS)",
    version="1.0.0",
    description="Resilient, serverless event-driven platform core for enterprise IT operations",
    lifespan=lifespan
)

# Configure Cross-Origin Resource Sharing (CORS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health & Container Readiness Probe
@app.get("/health", tags=["Health"])
def health_check():
    return {
        "status": "healthy",
        "service": "etms-core",
        "version": "1.0.0",
        "database": "connected"
    }


# Register Microservice Routers
app.include_router(tickets_router, prefix="/api/v1")
app.include_router(routing_router, prefix="/api/v1")
app.include_router(sla_router, prefix="/api/v1")
app.include_router(audit_router, prefix="/api/v1")
app.include_router(notifications_router, prefix="/api/v1")
app.include_router(search_router, prefix="/api/v1")
app.include_router(settings_router, prefix="/api/v1")

# Mount Static Frontend Assets
public_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "public")
if os.path.exists(public_dir):
    app.mount("/", StaticFiles(directory=public_dir, html=True), name="public")

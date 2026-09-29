"""
app/main.py — Main FastAPI Application Entrypoint & Static Frontend Mounting
"""
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.api.router import api_router
from app.db.init_db import init_database
from app.models.schemas import HealthResponse, ProblemDetail


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize DB schema & seeds
    init_database()
    yield


app = FastAPI(
    title="Digital Savings Account Opening Platform",
    description="Enterprise Straight-Through Processing (STP) Digital Customer Onboarding Platform with Distributed Saga Orchestration Engine",
    version="1.0.0",
    lifespan=lifespan
)

# CORS Middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# -----------------------------------------------------------------------------
# RFC-7807 Structured Problem Details Exception Handlers
# -----------------------------------------------------------------------------
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(
        request: Request, exc: StarletteHTTPException):
    problem = ProblemDetail(
        type=f"https://errors.enterprise-bank.com/{exc.status_code}",
        title=exc.detail if isinstance(exc.detail, str) else "HTTP Error",
        status=exc.status_code,
        detail=str(exc.detail),
        instance=str(request.url.path)
    )
    return JSONResponse(
        status_code=exc.status_code,
        content=problem.model_dump(),
        media_type="application/problem+json"
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
        request: Request, exc: RequestValidationError):
    invalid_params = [{"loc": list(e["loc"]),
                       "msg": e["msg"],
                       "type": e["type"]} for e in exc.errors()]
    problem = ProblemDetail(
        type="https://errors.enterprise-bank.com/400-validation-error",
        title="Bad Request - Payload Validation Error",
        status=status.HTTP_400_BAD_REQUEST,
        detail="The request payload failed schema validation against the API contract specification.",
        instance=str(request.url.path),
        invalid_params=invalid_params
    )
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content=problem.model_dump(),
        media_type="application/problem+json"
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    problem = ProblemDetail(
        type="https://errors.enterprise-bank.com/500-internal-server-error",
        title="Internal Server Error",
        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail=str(exc) or "An unhandled enterprise server error occurred.",
        instance=str(request.url.path)
    )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=problem.model_dump(),
        media_type="application/problem+json"
    )


# -----------------------------------------------------------------------------
# Health Probe Endpoint
# -----------------------------------------------------------------------------
@app.get(
    "/health",
    response_model=HealthResponse,
    tags=["System"],
    summary="Container Health and Readiness Probe"
)
def health_check():
    return HealthResponse()


# -----------------------------------------------------------------------------
# Mount REST API Router
# -----------------------------------------------------------------------------
app.include_router(api_router)


# -----------------------------------------------------------------------------
# Mount Static Frontend Assets at Root
# -----------------------------------------------------------------------------
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
public_dir = os.path.join(base_dir, "public")

if os.path.exists(public_dir):
    pages_dir = os.path.join(public_dir, "pages")
    if os.path.exists(pages_dir):
        app.mount("/pages", StaticFiles(directory=pages_dir), name="pages")

    js_dir = os.path.join(public_dir, "js")
    if os.path.exists(js_dir):
        app.mount("/js", StaticFiles(directory=js_dir), name="js")

    css_dir = os.path.join(public_dir, "css")
    if os.path.exists(css_dir):
        app.mount("/css", StaticFiles(directory=css_dir), name="css")

    app.mount("/", StaticFiles(directory=public_dir, html=True), name="public")

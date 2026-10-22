"""
app/main.py — FastAPI Application Entrypoint for Agent Evaluation Platform.
Monolith serving static frontend and exposing RFC 7807 compliant REST APIs.
"""
import os
from pathlib import Path
from fastapi import FastAPI, Request, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError

from app.database import init_db
from app.routes import health, agents, datasets, runs, trajectories, annotations, telemetry

app = FastAPI(
    title="Agent Evaluation Platform API",
    description="Enterprise Multi-Tier AI Agent Benchmark and Trajectory Evaluation Platform",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# RFC 7807 Global Exception Handlers
# ---------------------------------------------------------------------------
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    titles = {
        400: "Bad Request",
        401: "Unauthorized",
        403: "Forbidden",
        404: "Not Found",
        409: "Conflict",
        422: "Unprocessable Entity",
        500: "Internal Server Error"
    }
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "type": "about:blank",
            "title": titles.get(exc.status_code, "Error"),
            "status": exc.status_code,
            "detail": exc.detail,
            "instance": str(request.url.path)
        },
        headers={"Content-Type": "application/problem+json"}
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = exc.errors()
    detail_msg = errors[0].get("msg", "Validation error") if errors else "Invalid request payload"
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "type": "about:blank",
            "title": "Bad Request",
            "status": 400,
            "detail": detail_msg,
            "instance": str(request.url.path)
        },
        headers={"Content-Type": "application/problem+json"}
    )

# ---------------------------------------------------------------------------
# Router Inclusions
# ---------------------------------------------------------------------------
app.include_router(health.router)
app.include_router(agents.router)
app.include_router(datasets.router)
app.include_router(runs.router)
app.include_router(trajectories.router)
app.include_router(annotations.router)
app.include_router(telemetry.router)

# ---------------------------------------------------------------------------
# Static Files & UI Mounting
# ---------------------------------------------------------------------------
static_dir = Path(__file__).resolve().parent / "static"
static_dir.mkdir(parents=True, exist_ok=True)

app.mount("/", StaticFiles(directory=str(static_dir), html=True), name="static")

@app.on_event("startup")
def startup_event():
    """Ensure database schema and initial lookup data are initialized."""
    init_db(force_reseed=False)

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")
    uvicorn.run("app.main:app", host=host, port=port, reload=True)

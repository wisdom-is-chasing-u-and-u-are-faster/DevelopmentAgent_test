import os
from datetime import datetime, timezone
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.db.init_db import init_database
from app.api.products import router as products_router
from app.api.shade_finder import router as shade_finder_router
from app.api.cart import router as cart_router
from app.api.checkout import router as checkout_router
from app.api.subscriptions import router as subscriptions_router
from app.api.account import router as account_router

app = FastAPI(
    title="Enterprise D2C Online Cosmetic Store Platform API",
    version="1.0.0",
    description="MACH Composable Commerce backend powering hyper-personalized shade matching and subscriptions."
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    init_database()


@app.get("/health", tags=["Health"])
def health_check():
    return {
        "status": "ok",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "service": "cosmetics-store-platform"
    }


# Include API Routers
app.include_router(products_router, prefix="/api/v1")
app.include_router(shade_finder_router, prefix="/api/v1")
app.include_router(cart_router, prefix="/api/v1")
app.include_router(checkout_router, prefix="/api/v1")
app.include_router(subscriptions_router, prefix="/api/v1")
app.include_router(account_router, prefix="/api/v1")

# Mount Static UI Files
if os.path.exists("public"):
    if os.path.exists("public/pages"):
        app.mount("/pages", StaticFiles(directory="public/pages"), name="pages")
    if os.path.exists("public/js"):
        app.mount("/js", StaticFiles(directory="public/js"), name="js")
    app.mount("/", StaticFiles(directory="public", html=True), name="public")

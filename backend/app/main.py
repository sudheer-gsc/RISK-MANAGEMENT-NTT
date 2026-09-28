from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from .database import Base, engine
from .routes.fields import router as fields_router
from .routes.machines import router as machines_router
from .routes.prediction import router as prediction_router


# ======================================================
# PATHS
# ======================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

FRONTEND_DIR = PROJECT_ROOT / "frontend"


# ======================================================
# DATABASE
# ======================================================

Base.metadata.create_all(bind=engine)


# ======================================================
# FASTAPI APPLICATION
# ======================================================

app = FastAPI(
    title="Dynamic Machine Risk Prediction API",
    version="1.0.0",
    description=(
        "Local machine management and "
        "risk prediction system"
    ),
)


# ======================================================
# CORS
# ======================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8000",
        "http://127.0.0.1:8000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ======================================================
# API ROUTES
# ======================================================

app.include_router(fields_router)
app.include_router(machines_router)
app.include_router(prediction_router)


# ======================================================
# FRONTEND STATIC FILES
# ======================================================

app.mount(
    "/static",
    StaticFiles(directory=FRONTEND_DIR),
    name="static",
)


# ======================================================
# FRONTEND HOME PAGE
# ======================================================

@app.get("/")
def root():
    return FileResponse(
        FRONTEND_DIR / "index.html"
    )


# ======================================================
# HEALTH CHECK
# ======================================================

@app.get("/health")
def health():
    return {
        "status": "healthy"
    }
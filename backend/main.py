from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from backend.core.config import settings
from backend.core.database import engine, Base

# Import routers
from backend.api.v1 import health, datasets, jobs, artifacts, copilot

# Configure structured logging
logging.basicConfig(level=settings.LOG_LEVEL, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")

# Create tables for v1
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Intelligent Data Preprocessing Platform API",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, prefix="/api/v1")
app.include_router(datasets.router, prefix="/api/v1")
app.include_router(jobs.router, prefix="/api/v1")
app.include_router(artifacts.router, prefix="/api/v1")
app.include_router(copilot.router, prefix="/api/v1/copilot")
app.include_router(planner.router, prefix="/api/v1/planner")
app.include_router(automl.router, prefix="/api/v1/automl")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

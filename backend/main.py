from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging

from backend.core.config import settings
from backend.core.database import engine, Base

# Import routers
from backend.api.v1 import health, datasets, jobs, artifacts, copilot, planner, automl

# Configure structured logging
logging.basicConfig(level=settings.LOG_LEVEL, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")

# Create tables for v1
Base.metadata.create_all(bind=engine)

print(f"\n==================================================")
print(f"ProcessIQ Platform Services Started!")
print(f"STORAGE PROVIDER: {settings.STORAGE_PROVIDER.upper()}")
print(f"==================================================\n")

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Intelligent Data Preprocessing Platform API",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Global handler so unhandled exceptions still return a JSON response WITH CORS
# headers (Starlette's ServerErrorMiddleware would otherwise return a bare 500
# that bypasses the CORSMiddleware, which is what caused the browser CORS error).
@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logging.getLogger(__name__).exception("Unhandled exception", exc_info=exc)
    detail = str(exc) or exc.__class__.__name__
    return JSONResponse(status_code=500, content={"detail": detail})

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

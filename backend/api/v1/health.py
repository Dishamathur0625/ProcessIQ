from fastapi import APIRouter
from backend.core.config import settings
from backend.core.database import engine
import redis
from datetime import datetime

router = APIRouter(tags=["Health"])

@router.get("/health")
def health_check():
    response = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat()
    }
    
    # Check Database
    try:
        with engine.connect() as connection:
            response["database"] = "connected"
    except Exception as e:
        response["database"] = f"error: {str(e)}"
        response["status"] = "degraded"
        
    # Check Redis
    try:
        r = redis.from_url(settings.REDIS_URL)
        r.ping()
        response["redis"] = "connected"
    except Exception as e:
        response["redis"] = f"error: {str(e)}"
        response["status"] = "degraded"
        
    # Check Storage
    try:
        from backend.services.storage.factory import StorageFactory
        storage = StorageFactory.get_backend()
        response["storage"] = f"connected ({settings.STORAGE_PROVIDER})"
    except Exception as e:
        response["storage"] = f"error: {str(e)}"
        response["status"] = "degraded"
        
    # Check Gemini
    if settings.GEMINI_API_KEY:
        response["gemini"] = "configured"
    else:
        response["gemini"] = "missing_api_key"
        
    response["planner"] = "ready"
    response["automl"] = "ready"
    
    return response

@router.get("/ready")
def ready_check():
    return {"status": "ready"}
    
@router.get("/metrics")
def metrics():
    return {"status": "Metrics placeholder"}

from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "ProcessIQ Platform Services"
    ENVIRONMENT: str = "development"
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/processiq"
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # Storage
    STORAGE_PROVIDER: str = "supabase" # 'local' or 'supabase'
    SUPABASE_URL: str = ""
    SUPABASE_ANON_KEY: str = ""
    SUPABASE_SERVICE_ROLE_KEY: str = ""
    
    SUPABASE_BUCKET_DATASETS: str = "datasets"
    SUPABASE_BUCKET_PROCESSED: str = "processed"
    SUPABASE_BUCKET_MODELS: str = "models"
    SUPABASE_BUCKET_REPORTS: str = "reports"
    SUPABASE_BUCKET_ARTIFACTS: str = "artifacts"
    SUPABASE_BUCKET_VISUALIZATIONS: str = "visualizations"
    SUPABASE_BUCKET_MANIFESTS: str = "manifests"
    
    # Local Storage defaults
    UPLOAD_DIR: str = "storage/uploads"
    REPORT_DIR: str = "storage/reports"
    ARTIFACT_DIR: str = "storage/artifacts"
    
    MAX_UPLOAD_MB: int = 500
    LOG_LEVEL: str = "INFO"
    
    # Copilot settings
    LLM_PROVIDER: str = "gemini"
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-2.5-flash"
    
    # AutoML
    DEFAULT_RANDOM_SEED: int = 42
    MAX_PARALLEL_JOBS: int = 4
    
    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()

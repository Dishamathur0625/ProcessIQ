from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "ProcessIQ"
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/processiq"
    
    class Config:
        env_file = ".env"

settings = Settings()

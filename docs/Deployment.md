# Deployment Guide

ProcessIQ is designed to run its heavy compute natively on a host machine while persisting data to the cloud via Supabase.

## Prerequisites
- Python 3.10+
- Node.js 18+
- Docker & Docker Compose
- Supabase Project (PostgreSQL & Storage)
- Gemini API Key

## Configuration
Copy `.env.example` to `.env` and fill in the values:
- `DATABASE_URL`: Your Supabase PostgreSQL Connection String
- `SUPABASE_URL`: Your Supabase Project URL
- `SUPABASE_SERVICE_ROLE_KEY`: Your Supabase Service Key
- `STORAGE_PROVIDER`: Set to `supabase` for cloud storage, or `local` for local disk.

## Running the Application
We provide batch scripts to boot the infrastructure effortlessly.

1. **Boot the Backend**:
   Run `scripts/start_backend.bat`. This starts `uvicorn` natively.
   
2. **Boot the Frontend**:
   Run `scripts/start_frontend.bat`. This starts the Next.js dev server.
   
3. **Boot Everything**:
   Run `scripts/start_all.bat`. This will automatically boot Redis via Docker and launch the native backend and frontend in separate processes.

## Health Verification
Navigate to `http://localhost:8000/api/v1/health`. 
A fully healthy system using Supabase will return:
```json
{
    "status": "healthy",
    "database": "connected",
    "redis": "connected",
    "storage": "connected (supabase)",
    "gemini": "configured"
}
```

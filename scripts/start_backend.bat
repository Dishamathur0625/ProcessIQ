@echo off
echo Starting ProcessIQ Backend (FastAPI)...
echo Make sure Redis is running via Docker!
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload

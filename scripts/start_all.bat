@echo off
echo Starting ProcessIQ Infrastructure...
docker-compose up -d redis

echo Starting Backend...
start cmd /k "scripts\start_backend.bat"

echo Starting Frontend...
start cmd /k "scripts\start_frontend.bat"

echo All services starting!

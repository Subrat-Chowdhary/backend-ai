@echo off
echo ========================================
echo AI-Powered Resume Matching System
echo ========================================
echo.

echo Checking Docker...
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Docker is not installed or not running
    echo Please install Docker Desktop and make sure it's running
    pause
    exit /b 1
)

echo Docker found! Starting services...
echo.

echo Starting all services with Docker Compose...
docker-compose up -d

if %errorlevel% neq 0 (
    echo ERROR: Failed to start services
    echo Make sure Docker Desktop is running
    pause
    exit /b 1
)

echo.
echo ========================================
echo Services started successfully!
echo ========================================
echo.
echo Access points:
echo - API Documentation: http://localhost:8000/docs
echo - Health Check: http://localhost:8000/health
echo - MinIO Console: http://localhost:9001
echo - Qdrant Dashboard: http://localhost:6333/dashboard
echo.
echo To view logs: docker-compose logs -f
echo To stop services: docker-compose down
echo.
pause
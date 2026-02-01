@echo off
REM Database setup script for InsightProfile
REM This script installs dependencies and runs database migrations

echo ========================================
echo InsightProfile Database Setup
echo ========================================
echo.

REM Activate virtual environment
echo [1/4] Activating virtual environment...
call venv\Scripts\activate.bat
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Virtual environment not found. Run setup_env.bat first.
    pause
    exit /b 1
)

REM Install/upgrade database dependencies
echo [2/4] Installing database dependencies...
pip install -q -U sqlalchemy psycopg2-binary alembic
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)

REM Check if PostgreSQL is running
echo [3/4] Checking PostgreSQL connection...
python -c "from database import check_db_connection; import sys; sys.exit(0 if check_db_connection() else 1)"
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo WARNING: PostgreSQL is not running or not accessible!
    echo.
    echo Please ensure PostgreSQL is running before proceeding.
    echo See POSTGRES_SETUP.md for installation instructions.
    echo.
    echo Options:
    echo   1. Install PostgreSQL manually
    echo   2. Use Docker: docker compose up -d
    echo.
    pause
    exit /b 1
)

echo PostgreSQL is running!

REM Run migrations
echo [4/4] Running database migrations...
alembic upgrade head
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Migration failed
    pause
    exit /b 1
)

echo.
echo ========================================
echo Database setup completed successfully!
echo ========================================
echo.
echo You can now start the API server:
echo   python -m uvicorn main:app --reload
echo.
pause

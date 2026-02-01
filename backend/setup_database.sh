#!/bin/bash
# Database setup script for InsightProfile (Linux/Mac)
# This script installs dependencies and runs database migrations

echo "========================================"
echo "InsightProfile Database Setup"
echo "========================================"
echo ""

# Activate virtual environment
echo "[1/4] Activating virtual environment..."
source venv/bin/activate
if [ $? -ne 0 ]; then
    echo "ERROR: Virtual environment not found. Run setup_env.sh first."
    exit 1
fi

# Install/upgrade database dependencies
echo "[2/4] Installing database dependencies..."
pip install -q -U sqlalchemy psycopg2-binary alembic
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to install dependencies"
    exit 1
fi

# Check if PostgreSQL is running
echo "[3/4] Checking PostgreSQL connection..."
python -c "from database import check_db_connection; import sys; sys.exit(0 if check_db_connection() else 1)"
if [ $? -ne 0 ]; then
    echo ""
    echo "WARNING: PostgreSQL is not running or not accessible!"
    echo ""
    echo "Please ensure PostgreSQL is running before proceeding."
    echo "See POSTGRES_SETUP.md for installation instructions."
    echo ""
    echo "Options:"
    echo "  1. Install PostgreSQL manually"
    echo "  2. Use Docker: docker compose up -d"
    echo ""
    exit 1
fi

echo "PostgreSQL is running!"

# Run migrations
echo "[4/4] Running database migrations..."
alembic upgrade head
if [ $? -ne 0 ]; then
    echo "ERROR: Migration failed"
    exit 1
fi

echo ""
echo "========================================"
echo "Database setup completed successfully!"
echo "========================================"
echo ""
echo "You can now start the API server:"
echo "  python -m uvicorn main:app --reload"
echo ""

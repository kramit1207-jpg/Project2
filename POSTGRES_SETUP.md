# PostgreSQL Setup Instructions

## Option 1: Using Docker (Recommended)

1. Install Docker Desktop for Windows from: https://www.docker.com/products/docker-desktop/
2. After installation, open PowerShell in the project directory and run:
   ```bash
   docker compose up -d
   ```
3. Verify PostgreSQL is running:
   ```bash
   docker compose ps
   ```

## Option 2: Manual PostgreSQL Installation

1. Download PostgreSQL 15 from: https://www.postgresql.org/download/windows/
2. Install with default settings
3. During installation, set password for `postgres` user to: `postgres`
4. Create database named `insightprofile`:
   ```sql
   CREATE DATABASE insightprofile;
   ```

## Verification

Once PostgreSQL is running, verify the connection:

```bash
# From project root
cd backend
.\venv\Scripts\Activate.ps1
python -c "from sqlalchemy import create_engine; engine = create_engine('postgresql://postgres:postgres@localhost:5432/insightprofile'); conn = engine.connect(); print('Connected successfully!'); conn.close()"
```

## Database Configuration

The application expects PostgreSQL to be running on:
- Host: `localhost`
- Port: `5432`
- Database: `insightprofile`
- Username: `postgres`
- Password: `postgres`

These settings can be changed in the `backend/.env` file.

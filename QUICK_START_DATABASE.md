# Quick Start Guide - PostgreSQL Integration

## 🚀 Get Started in 5 Minutes

### Step 1: Set Up PostgreSQL (Choose One)

**Option A: Docker (Easiest)**
```bash
docker compose up -d
```

**Option B: Manual PostgreSQL**
1. Download from https://www.postgresql.org/download/windows/
2. Install with default settings
3. Set password to: `postgres`
4. Create database: `insightprofile`

### Step 2: Install Backend Dependencies
```bash
cd backend
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### Step 3: Run Database Migrations
```bash
alembic upgrade head
```
*Or use: `setup_database.bat`*

### Step 4: Verify Database Connection
```bash
python -c "from database import check_db_connection; print('✓ Connected!' if check_db_connection() else '✗ Connection failed')"
```

### Step 5: Start the Application
```bash
# Start backend (from backend folder)
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Start frontend (new terminal, from frontend folder)
npm run dev
```

## ✅ Verify It's Working

### Test Cache Miss (First Request)
```bash
curl -X POST http://localhost:8000/api/analyze \
  -H "Content-Type: application/json" \
  -d "{\"linkedin_url\": \"https://www.linkedin.com/in/example\"}"
```
**Expected**: Takes ~35-40 seconds, returns `"cached": false`

### Test Cache Hit (Second Request)
```bash
curl -X POST http://localhost:8000/api/analyze \
  -H "Content-Type: application/json" \
  -d "{\"linkedin_url\": \"https://www.linkedin.com/in/example\"}"
```
**Expected**: Takes <1 second, returns `"cached": true`

### Check Database Stats
```bash
curl http://localhost:8000/health
```
**Expected**: Shows `"database": "connected"` and statistics

## 📊 What You Get

- ⚡ **35-40x faster** responses for cached profiles
- 💰 **Reduced API costs** - no repeated calls
- 📈 **Data persistence** - historical analysis preserved
- 🔄 **Auto-refresh** - cache expires after 30 days
- 🛡️ **Graceful degradation** - works even if DB is down

## 🔧 Common Issues

**"Connection failed"**
- Check PostgreSQL is running: `docker compose ps`
- Verify DATABASE_URL in `.env` file

**"Table does not exist"**
- Run migrations: `alembic upgrade head`

**"Module not found"**
- Activate venv: `.\venv\Scripts\Activate.ps1`
- Install deps: `pip install -r requirements.txt`

## 📚 More Information

- **Setup Details**: `POSTGRES_SETUP.md`
- **Testing Guide**: `TESTING_DATABASE.md`
- **Full Documentation**: `README.md`
- **Implementation Summary**: `DATABASE_INTEGRATION_SUMMARY.md`

## 🎉 Success!

If you see `"cached": true` in your second request, the integration is working perfectly!

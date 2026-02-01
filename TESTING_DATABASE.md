# Database Caching - Testing Guide

This guide covers how to test the PostgreSQL caching functionality of InsightProfile.

## Prerequisites

1. PostgreSQL must be running (see `POSTGRES_SETUP.md`)
2. Database migrations must be applied:
   ```bash
   cd backend
   .\venv\Scripts\Activate.ps1  # Windows
   # or: source venv/bin/activate  # Linux/Mac
   alembic upgrade head
   ```

## Test Cases

### Test 1: Fresh Profile (Cache Miss)

**Objective**: Test that a new LinkedIn profile is fetched from APIs and cached.

**Steps**:
1. Start the backend server:
   ```bash
   cd backend
   .\venv\Scripts\Activate.ps1
   python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

2. Make a request with a LinkedIn URL:
   ```bash
   curl -X POST http://localhost:8000/api/analyze \
     -H "Content-Type: application/json" \
     -d '{"linkedin_url": "https://www.linkedin.com/in/example"}'
   ```

3. **Expected Result**:
   - Response includes `"cached": false`
   - Processing takes ~35-40 seconds (Humantic wait time)
   - Data is stored in database

4. **Verify in Database**:
   ```sql
   SELECT linkedin_url, user_id, created_at 
   FROM humantic_profiles 
   ORDER BY created_at DESC LIMIT 1;
   
   SELECT summary, created_at 
   FROM gemini_analyses 
   ORDER BY created_at DESC LIMIT 1;
   ```

### Test 2: Cached Profile (Cache Hit)

**Objective**: Verify that subsequent requests for the same profile return cached data.

**Steps**:
1. Make the same request again:
   ```bash
   curl -X POST http://localhost:8000/api/analyze \
     -H "Content-Type: application/json" \
     -d '{"linkedin_url": "https://www.linkedin.com/in/example"}'
   ```

2. **Expected Result**:
   - Response includes `"cached": true`
   - Response includes `"cached_at"` timestamp
   - Response is instant (< 1 second)
   - No external API calls made

3. **Verify in Logs**:
   Look for: `Cache hit: https://www.linkedin.com/in/example`

### Test 3: Force Refresh

**Objective**: Test bypassing cache to fetch fresh data.

**Steps**:
1. Make a request with `force_refresh=true`:
   ```bash
   curl -X POST "http://localhost:8000/api/analyze?force_refresh=true" \
     -H "Content-Type: application/json" \
     -d '{"linkedin_url": "https://www.linkedin.com/in/example"}'
   ```

2. **Expected Result**:
   - Response includes `"cached": false`
   - Processing takes ~35-40 seconds again
   - Old cache entry is replaced with new data

### Test 4: Cache Expiry

**Objective**: Verify that expired profiles are not served from cache.

**Steps**:
1. Manually update a profile's `created_at` to 31 days ago:
   ```sql
   UPDATE humantic_profiles 
   SET created_at = NOW() - INTERVAL '31 days'
   WHERE linkedin_url = 'https://www.linkedin.com/in/example';
   ```

2. Make a request for that profile:
   ```bash
   curl -X POST http://localhost:8000/api/analyze \
     -H "Content-Type: application/json" \
     -d '{"linkedin_url": "https://www.linkedin.com/in/example"}'
   ```

3. **Expected Result**:
   - Cache miss (expired)
   - Fresh data fetched from APIs
   - New cache entry created

### Test 5: Clear Cache Endpoint

**Objective**: Test the cache clearing functionality.

**Steps**:
1. Clear cache for a specific profile:
   ```bash
   curl -X DELETE "http://localhost:8000/api/cache/https://www.linkedin.com/in/example"
   ```

2. **Expected Result**:
   - Response: `{"message": "Cache cleared for ..."}`
   - Profile and analyses deleted from database

3. Verify deletion:
   ```bash
   curl -X POST http://localhost:8000/api/analyze \
     -H "Content-Type: application/json" \
     -d '{"linkedin_url": "https://www.linkedin.com/in/example"}'
   ```
   - Should be cache miss

### Test 6: Health Endpoint

**Objective**: Verify database connectivity monitoring.

**Steps**:
1. Check health with database running:
   ```bash
   curl http://localhost:8000/health
   ```

2. **Expected Result**:
   ```json
   {
     "status": "healthy",
     "database": "connected",
     "stats": {
       "total_profiles": 5,
       "total_analyses": 5,
       "recent_profiles_7_days": 3,
       "timestamp": "2026-01-29T..."
     }
   }
   ```

3. Stop PostgreSQL and check again:
   ```bash
   curl http://localhost:8000/health
   ```

4. **Expected Result**:
   ```json
   {
     "status": "degraded",
     "database": "disconnected",
     "error": "..."
   }
   ```

### Test 7: Database Connection Failure (Graceful Degradation)

**Objective**: Ensure app continues to work without database.

**Steps**:
1. Stop PostgreSQL:
   ```bash
   docker compose down  # if using Docker
   # or: stop PostgreSQL service
   ```

2. Make an analysis request:
   ```bash
   curl -X POST http://localhost:8000/api/analyze \
     -H "Content-Type: application/json" \
     -d '{"linkedin_url": "https://www.linkedin.com/in/example"}'
   ```

3. **Expected Behavior**:
   - App should log database errors but continue
   - APIs are still called
   - Response doesn't include `cached` field
   - Analysis completes successfully

## Performance Metrics

### Without Caching
- First request: 35-40 seconds
- Subsequent requests: 35-40 seconds each

### With Caching
- First request: 35-40 seconds (cache miss)
- Subsequent requests: < 1 second (cache hit)
- **Improvement**: ~35-40x faster for cached profiles

## Monitoring Cache Usage

Check database statistics:
```bash
curl http://localhost:8000/health | jq .stats
```

View all cached profiles:
```sql
SELECT 
    linkedin_url,
    created_at,
    (SELECT COUNT(*) FROM gemini_analyses WHERE humantic_profile_id = hp.id) as analysis_count
FROM humantic_profiles hp
ORDER BY created_at DESC;
```

## Troubleshooting

### "Database connection failed"
- Ensure PostgreSQL is running: `docker compose ps`
- Check connection string in `.env`: `DATABASE_URL=postgresql://...`
- Verify credentials are correct

### "Table does not exist"
- Run migrations: `alembic upgrade head`
- Check migration status: `alembic current`

### Cache not working
- Check logs for database errors
- Verify `crud.py` functions are being called
- Check if `Depends(get_db)` is in the endpoint

### Slow queries
- Ensure indexes are created (check migration file)
- Run `EXPLAIN ANALYZE` on slow queries
- Consider adding more indexes if needed

## Success Criteria

✓ Fresh profiles are cached after first request  
✓ Cached profiles return instantly  
✓ Force refresh bypasses cache  
✓ Expired profiles are refreshed  
✓ Cache can be cleared via API  
✓ Health endpoint shows database status  
✓ App continues to work if database is down  
✓ Statistics are tracked and queryable  

## Next Steps

After testing, consider:
1. Adding cache warming (pre-fetch popular profiles)
2. Implementing background refresh for expiring profiles
3. Adding admin UI for cache management
4. Setting up database backups
5. Adding database connection pooling monitoring

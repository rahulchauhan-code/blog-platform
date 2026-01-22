# Production Deployment Guide - PostgreSQL Data Loss & LibreTranslate Fixes

## Summary of Changes

This guide documents the critical fixes applied to address two production issues on Render:
1. **PostgreSQL Data Loss** - Users and blog posts disappearing after redeploy
2. **LibreTranslate Translation Failures** - Translation not working on Render

---

## Issue #1: PostgreSQL Data Loss - ROOT CAUSE & FIX

### Problem
The application was using `db.create_all()` in the production code path, which:
- Recreates tables on every deploy/restart
- Drops existing data when schemas are altered
- Bypasses proper database migrations
- Is extremely dangerous in production with PostgreSQL

### Root Cause in Original Code
```python
# app.py - DANGEROUS CODE (OLD)
with app.app_context():
    from sqlalchemy import inspect
    inspector = inspect(db.engine)
    tables = inspector.get_table_names()
    if not tables:
        db.create_all()  # ❌ UNSAFE - Recreates tables, loses data on redeploy
```

### Solution Applied

#### 1. **Removed `db.create_all()` from app.py**
   - ✅ Changed to only verify tables exist
   - ✅ Relies on Flask-Migrate for schema management
   - ✅ Data persists across redeploys

**New Code (app.py):**
```python
# Database initialization: Flask-Migrate handles all schema management
# IMPORTANT: Do NOT use db.create_all() in production
with app.app_context():
    try:
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        if tables:
            logger.info('Database initialized with tables: %s', tables)
        else:
            logger.warning('No tables found. Ensure migrations are applied.')
    except Exception as e:
        logger.exception(f"Error checking database tables: {str(e)}")
```

#### 2. **Updated config.py - Enforce SSL for PostgreSQL**
   - ✅ Automatically appends `?sslmode=require` to PostgreSQL URLs
   - ✅ Secure connection to Render PostgreSQL
   - ✅ Prevents man-in-the-middle attacks

**New Code (config.py):**
```python
# For Render production: append sslmode=require if PostgreSQL
if _db_url and 'postgresql://' in _db_url and 'sslmode' not in _db_url:
    _db_url = _db_url.rstrip('/') + '?sslmode=require'

SQLALCHEMY_DATABASE_URI = _db_url or 'sqlite:///blog.db'
```

#### 3. **Updated render.yaml - Enable Flask-Migrate**
   - ✅ Runs `flask db upgrade` before starting the app
   - ✅ Applies all pending migrations
   - ✅ Prevents app startup if migrations fail

**New Code (render.yaml):**
```yaml
startCommand: flask db upgrade && gunicorn wsgi:app --workers 2 --threads 2 --timeout 60 --bind 0.0.0.0:$PORT
```

### Step 1: Initialize Flask-Migrate (One-Time Setup)

If migrations folder doesn't exist, run this locally:

```bash
# From your project root
flask db init                    # Creates migrations/ folder
flask db migrate -m "Initial migration"  # Generates migration file
```

This will create:
- `migrations/` - Directory with version control
- `migrations/versions/` - Contains migration files
- `alembic.ini` - Migration configuration

### Step 2: Deploy to Render

When you push to Render:
1. Render builds the container
2. Runs: `flask db upgrade` (applies migrations)
3. Starts Gunicorn with the app
4. Data is preserved across restarts ✅

### Verification

After deployment, check that tables are created:

```bash
# Access Render console
flask shell

# Inside Flask shell
from models import db, User, Post
print(db.metadata.tables.keys())  # Should show: dict_keys(['users', 'post', 'post_content'])
```

---

## Issue #2: LibreTranslate Failures - ROOT CAUSE & FIX

### Problems on Render
1. **No API Key Support** - Public endpoint hammered by rate limits
2. **HTTP vs HTTPS** - Mixed protocols cause SSL errors
3. **Cloud IP Blocking** - Render's shared IPs may be blocked
4. **No Error Logging** - Failures hidden from Render logs
5. **Client-Side API Calls** - Exposed API endpoints to browsers

### Root Causes in Original Code
```python
# ISSUES IN OLD CODE:
1. api_key not read from environment
2. No HTTPS enforcement
3. Poor error handling
4. Fallback to MyMemory is good, but not properly logged
5. Cache mechanism could hide real errors
```

### Solution Applied: Complete Refactor

#### New Features in `services/translation_service.py`

##### 1. **Environment Variable API Key Support**
```python
# NOW: Reads API key from environment first
api_url = os.environ.get('TRANSLATION_API_URL') or current_app.config.get('TRANSLATION_API_URL', '')
api_key = os.environ.get('TRANSLATION_API_KEY') or current_app.config.get('TRANSLATION_API_KEY', '')
```

**Set in Render:**
```
Environment Variables:
TRANSLATION_API_URL: https://api.libretranslate.de/translate
TRANSLATION_API_KEY: your_api_key_here
```

##### 2. **HTTPS Enforcement**
```python
# Enforce HTTPS for production security
if not api_url.startswith('https://'):
    logger.warning(f"LibreTranslate URL must use HTTPS; got: {api_url}")
    api_url = api_url.replace('http://', 'https://')
```

##### 3. **Comprehensive Error Logging for Render**
Every failure is logged with context:
- Status codes
- Timeouts
- Connection errors
- IP blocking indicators
- Rate limiting

```python
logger.error(f"LibreTranslate returned {response.status_code}: {response.text[:200]}")
logger.error(f"LibreTranslate timeout (5s): {e}")
logger.error(f"LibreTranslate connection error (possible IP block or DNS issue): {e}")
```

##### 4. **Proper Rate Limit Handling**
- Detects 429 Too Many Requests
- Activates 60-second cooldown
- Fallback to MyMemory automatically
- Prevents cascading failures

```python
if response.status_code == 429:
    logger.error("LibreTranslate rate limit exceeded (429)")
    global _last_rate_limit_hit
    _last_rate_limit_hit = time.time()
    # Falls back to MyMemory - no broken translation
```

##### 5. **Backend-Only Translation**
- All translation calls originate from server
- No client-side API access
- API keys never exposed to browsers
- MyMemory as secure fallback

---

## Configuration Guide

### 1. Set Environment Variables in Render

Go to your Render service dashboard:
**Settings → Environment Variables**

```
DATABASE_URL:         (Render auto-generates this)
SECRET_KEY:           your-secret-key-here
TRANSLATION_ENABLED:  true
TRANSLATION_API_URL:  https://api.libretranslate.de/translate
TRANSLATION_API_KEY:  your_api_key_here
```

### 2. Verify Configuration

Add this debug endpoint to check current setup:

```bash
curl https://your-render-app.onrender.com/health
# Response: {"status": "ok"}
```

### 3. Monitor Errors in Render Logs

Render Logs Panel shows all translation errors:

```
ERROR:services.translation_service:LibreTranslate timeout (5s): ...
ERROR:services.translation_service:LibreTranslate rate limit exceeded (429)
INFO:services.translation_service:MyMemory translation succeeded: '...'
```

---

## Testing Locally Before Deploy

### 1. Test Database Migrations

```bash
# Create test migration
flask db migrate -m "Test migration"

# Verify migration file created in migrations/versions/
# Edit if needed for manual migrations

# Test upgrade locally
flask db upgrade

# Verify tables exist
flask shell
>>> from models import db, User, Post, PostContent
>>> db.metadata.tables.keys()
```

### 2. Test Translation with API Key

```bash
# Create .env file locally
echo "TRANSLATION_API_KEY=your_test_key" >> .env
echo "TRANSLATION_API_URL=https://api.libretranslate.de/translate" >> .env

# Test Flask app
python app.py
# Visit http://localhost:5000 and try translation

# Check logs for successful translation:
# INFO:services.translation_service:Backend translation initiated: text=Hello...
```

### 3. Test Without API Key (MyMemory Fallback)

```bash
# Unset API key to test fallback
export TRANSLATION_API_URL=""

# Run app
python app.py
# Translations should still work via MyMemory fallback
# Check logs: INFO:services.translation_service:MyMemory translation succeeded
```

---

## Deployment Checklist

- [ ] `migrations/` folder exists and is committed to Git
- [ ] Initial migration file created: `flask db migrate`
- [ ] All database changes are in migrations (never modify `.db` directly)
- [ ] Environment variables set in Render:
  - [ ] `DATABASE_URL` - Auto-set by Render
  - [ ] `TRANSLATION_API_URL` - Configured
  - [ ] `TRANSLATION_API_KEY` - Set (or empty for MyMemory fallback)
  - [ ] `SECRET_KEY` - Set to strong value
- [ ] `render.yaml` has correct startCommand with `flask db upgrade`
- [ ] Gunicorn entry point updated to `wsgi:app`
- [ ] `wsgi.py` fixed (`__name__` not `_name_`)
- [ ] Tested locally: `python app.py` works
- [ ] Tested locally: Translations work
- [ ] Git commit and push to trigger Render redeploy

---

## Render Redeploy Process

1. **Commit changes:**
   ```bash
   git add -A
   git commit -m "Fix: PostgreSQL data loss and LibreTranslate issues"
   git push origin main
   ```

2. **Monitor deployment:**
   - Render automatically detects new push
   - Builds Docker image
   - Runs: `flask db upgrade` (applies migrations)
   - Starts Gunicorn with new code
   - Check Logs panel for errors

3. **Verify success:**
   - App loads without 500 errors
   - Database tables exist (no re-creation)
   - Translation works (check logs)
   - User data persists across restart

---

## Troubleshooting

### Problem: `flask db upgrade` fails during deploy
**Solution:**
- Check migration file syntax
- Verify `migrations/` folder exists and is committed
- Run locally: `flask db upgrade` to catch errors early

### Problem: Translations still failing on Render
**Solution:**
- Check `TRANSLATION_API_KEY` is set
- Check logs for: `LibreTranslate connection error`
- Try MyMemory fallback: unset `TRANSLATION_API_URL`

### Problem: Data still disappearing
**Solution:**
- Verify `db.create_all()` removed from app.py ✅ (already done)
- Check migrations running: `flask db current`
- Ensure `flask db upgrade` runs before startup

### Problem: Gunicorn fails to start
**Solution:**
- Fix wsgi.py: `if __name__ == "__main__"` not `_name_`
- Verify: `gunicorn wsgi:app` works locally
- Check logs for import errors

---

## Files Modified

| File | Changes |
|------|---------|
| `app.py` | Removed `db.create_all()`, verify tables only |
| `config.py` | Added SSL enforcement (`sslmode=require`) |
| `wsgi.py` | Fixed Python syntax (`__name__` vs `_name_`) |
| `services/translation_service.py` | Complete refactor: env vars, HTTPS, error logging, backend-only |
| `render.yaml` | Updated startCommand to use `flask db upgrade && gunicorn wsgi:app` |

---

## Next Steps

1. **Local Testing:**
   ```bash
   cd your-project
   flask db migrate -m "Initial"
   flask db upgrade
   python app.py
   ```

2. **Deploy to Render:**
   ```bash
   git push origin main
   ```

3. **Monitor Render Logs:**
   - Check for database errors
   - Verify translations working
   - Confirm data persists on restart

4. **Production Validation:**
   - Create a test user and post
   - Restart Render service
   - Verify data still exists
   - Test translation feature

---

## Support & References

- **Flask-Migrate Docs:** https://flask-migrate.readthedocs.io/
- **PostgreSQL on Render:** https://render.com/docs/postgres
- **Gunicorn Config:** https://docs.gunicorn.org/en/latest/
- **LibreTranslate API:** https://libretranslate.com/docs
- **MyMemory API:** https://mymemory.translated.net/

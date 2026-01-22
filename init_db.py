"""Initialize database tables.

This helper is intentionally conservative: it will refuse to run in non-development
environments unless explicitly allowed via the ALLOW_INIT_DB env var. Use Flask-Migrate
for production schema management (`flask db migrate` / `flask db upgrade`).
"""
import os
from app import app, db

# Safety: prevent accidental use in production
if os.environ.get('FLASK_ENV', '').lower() != 'development' and os.environ.get('ALLOW_INIT_DB', '').lower() != 'true':
    raise SystemExit("Refusing to run db.create_all() in non-development environment. Set FLASK_ENV=development or ALLOW_INIT_DB=true to override.")

with app.app_context():
    db.create_all()
    print("✅ Database tables created successfully!")

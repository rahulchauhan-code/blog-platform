# Quick Start: Flask-Migrate Setup for Render

## ONE-TIME LOCAL SETUP (Required before first deploy)

Run these commands from your project root to initialize migrations:

```bash
# 1. Initialize Flask-Migrate (creates migrations folder)
flask db init

# 2. Create initial migration from current models
flask db migrate -m "Initial migration: users, posts, post_content tables"

# 3. Test the migration locally
flask db upgrade

# 4. Verify tables were created
flask shell
>>> from models import db
>>> db.metadata.tables.keys()
dict_keys(['users', 'post', 'post_content'])
>>> exit()

# 5. Commit to Git
git add migrations/
git commit -m "Initialize Flask-Migrate with initial schema"
git push origin main
```

## What This Does

- **flask db init**: Creates the `migrations/` folder with:
  - `env.py` - Migration environment config
  - `script.py.mako` - Migration template
  - `versions/` - Directory for migration files

- **flask db migrate**: Generates a migration file by comparing:
  - Current SQLAlchemy models in `models.py`
  - Current database schema
  - Creates `migrations/versions/xxxxx_initial_migration_users_posts.py`

- **flask db upgrade**: Applies all pending migrations to the database

## Render Deployment Flow

When you push to Render:

```
1. Git push triggers Render webhook
2. Render builds Docker image
3. Runs: flask db upgrade
   ↓ (applies all migrations/versions/*.py files)
4. Runs: gunicorn wsgi:app
   ↓ (starts the web server)
5. App is live with database schema synced
```

## Important: Future Changes to Models

If you add/modify models in `models.py`:

```bash
# 1. Generate migration for the change
flask db migrate -m "Add comment column to Post table"

# 2. Review the generated migration (optional editing)
# vim migrations/versions/xxxxx_add_comment_column.py

# 3. Test locally
flask db upgrade

# 4. Commit and push
git add migrations/versions/xxxxx_add_comment_column.py
git commit -m "Add migration: comment column"
git push origin main
```

Render automatically runs `flask db upgrade` at each deploy! ✅

## Troubleshooting

**Problem: `flask db init` says "Flask-Migrate already initialized"`
- Migrations folder already exists (good! Skip to step 2)

**Problem: `flask db migrate` shows no changes**
- Models might already be in database
- Check migration file was created in `migrations/versions/`

**Problem: `flask db upgrade` fails locally**
- SQL error in migration file
- Edit `migrations/versions/xxxxx_*.py` to fix
- Test again with `flask db upgrade`

**Problem: Render deploy fails with migration error**
- Check Render Logs panel for SQL error
- Fix migration file locally
- Git push again
- Render will retry with fixed migration

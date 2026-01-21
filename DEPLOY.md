Quick Deploy to Render

1) Push repository to GitHub (make sure `.gitignore` excludes secrets).

2) On Render:
   - New -> Web Service -> Connect GitHub repo
   - For Build Command use: `pip install -r requirements.txt`
   - For Start Command use: `flask db upgrade && gunicorn app:app --workers 2 --bind 0.0.0.0:$PORT`
   - Add Environment variables:
     - `DATABASE_URL` = your Postgres URI (e.g. the Render Postgres URI)
     - `SECRET_KEY` = strong random key
     - `TRANSLATION_API_URL`, `TRANSLATION_API_KEY` (optional)

3) Migrations:
   - The start command runs `flask db upgrade` on deploy; ensure the `migrations/` folder exists if you track migrations.

4) Verification:
   - Open the provided Render URL. Check logs in Render dashboard if the app fails to start.

Notes & Troubleshooting
- If psycopg2 fails to build, Render typically provides system libs; use `psycopg2-binary` in `requirements.txt` (already present).
- Do not commit `.env` or any credentials. Use Render environment variables.

Render deployment steps for `flask-blog-app`

Prerequisites
- A GitHub (or Git) remote with this repository pushed.
- A Render account (https://render.com).
- Optional: a Render PostgreSQL managed DB (recommended for production).

1) Prepare migrations locally
- Ensure `FLASK_APP` is set to `app.py`.
  - PowerShell:
    ```powershell
    $env:FLASK_APP='app.py'
    ```
- Initialize migrations (only once):
  ```powershell
  python -m flask db init
  ```
- Create an initial migration:
  ```powershell
  python -m flask db migrate -m "Initial migration"
  ```
- Apply locally to verify:
  ```powershell
  python -m flask db upgrade
  ```
- Commit the `migrations/` folder and push to your repo:
  ```powershell
  git add migrations
  git commit -m "Add initial migrations"
  git push
  ```

2) Create a managed Postgres DB on Render (recommended)
- In Render dashboard: New -> PostgreSQL
- Choose plan; create the DB. Render will provide a `DATABASE_URL` connection string.
- Note: Render automatically sets `DATABASE_URL` for services in the same account if linked; if not, copy it for the next step.

3) Create the Web Service on Render
- New -> Web Service -> Connect your Git repo & branch
- Environment: `Python`
- Build Command: (leave default or)
  ```bash
  pip install -r requirements.txt
  ```
- Start Command: (we recommend running migrations then starting Gunicorn)
  ```bash
  flask db upgrade && gunicorn app:app --workers 1 --timeout 60 --bind 0.0.0.0:$PORT
  ```
  Note: `Procfile` already contains this start command as `web:` entry.

4) Set Environment Variables in Render (Service -> Environment)
- `SECRET_KEY` = a secure random string
- `FLASK_ENV` = `production` (or set `FLASK_CONFIG=production` if you prefer)
- `TRANSLATION_API_URL` and `TRANSLATION_API_KEY` if used
- (Optional) any other config keys your app needs
- `DATABASE_URL` should be set automatically if you used Render Postgres; otherwise paste the connection string.

5) Deploy and verify
- Trigger a deploy (Render will build the app).
- Check service logs on Render: you should see `flask db upgrade` run and `Gunicorn` start.
- Use the `/health` endpoint to verify the app:
  - `https://<your-service>.onrender.com/health` should return `{"status":"ok"}`
- If there are issues, view the logs and fix missing env vars or dependency problems.

6) Notes and tips
- Do NOT rely on SQLite (`instance/blog.db`) in Render production — Render's filesystem is ephemeral; use Postgres.
- Keep migrations in source control and run `flask db upgrade` as part of the start command or deployment hooks.
- For database admin access, use the Render dashboard's connection info to connect with a client.

Example Procfile (already present):
```
web: flask db upgrade && gunicorn app:app --workers 1 --timeout 60 --bind 0.0.0.0:$PORT
```

If you want, I can:
- Add a `render.yaml` (I see an example already) with the correct `startCommand` and `envVars` filled.
- Create and commit migrations locally for you (I can run `flask db init/migrate` here and add files), then push — do you want me to generate and commit the initial migration now?

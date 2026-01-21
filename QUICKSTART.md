# Flask Blog Application - Quick Start Guide

## Quick Start (Windows)

1. **Run the deployment script:**
   ```cmd
   deploy.bat
   ```

2. **Configure the application:**
   - Edit `.env` file with your database credentials
   - Update `SECRET_KEY` with a secure random string

3. **Start the application:**
   ```cmd
   python app.py
   ```

4. **Access the application:**
   - Open browser and navigate to: http://localhost:5000

## Quick Start (Linux/Mac)

1. **Make deployment script executable:**
   ```bash
   chmod +x deploy.sh
   ```

2. **Run the deployment script:**
   ```bash
   ./deploy.sh
   ```

3. **Configure the application:**
   - Edit `.env` file with your database credentials
   - Update `SECRET_KEY` with a secure random string

4. **Start the application:**
   ```bash
   python app.py
   ```

5. **Access the application:**
   - Open browser and navigate to: http://localhost:5000

## Manual Setup

### 1. Create Virtual Environment
```bash
python -m venv venv
```

### 2. Activate Virtual Environment

**Windows:**
```cmd
venv\Scripts\activate
```

**Linux/Mac:**
```bash
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment
```bash
# Windows
copy .env.example .env

# Linux/Mac
cp .env.example .env
```

Edit `.env` file with your settings.

### 5. Initialize Database

**Option A: Using Flask-Migrate (Recommended)**
```bash
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

**Option B: Direct Creation (Development only)**
```python
python
>>> from app import app, db
>>> with app.app_context():
...     db.create_all()
>>> exit()
```

### 6. Run Application
```bash
python app.py
```

## First Time Usage

1. **Register an account:**
   - Go to http://localhost:5000/auth/register
   - Fill in your details
   - Click "Register"

2. **Login:**
   - Go to http://localhost:5000/auth/login
   - Enter your credentials
   - Click "Login"

3. **Create your first post:**
   - Click "Create Post" in navigation
   - Fill in title, content, and category
   - Select "Published" status
   - Click "Create Post"

4. **Test translation:**
   - Use language selector in navigation
   - Select different languages
   - Watch your content translate!

## Common Commands

### Run Development Server
```bash
python app.py
# or
flask run
```

### Create Database Migration
```bash
flask db migrate -m "Description of changes"
flask db upgrade
```

### Run with Debug Mode
```bash
export FLASK_ENV=development  # Linux/Mac
set FLASK_ENV=development     # Windows
python app.py
```

## Troubleshooting

### Port Already in Use
```bash
# Change port in .env
SERVER_PORT=5001
```

### Database Connection Error
- Check Oracle Database is running
- Verify credentials in `.env`
- Test connection with SQL Developer or similar tool

### Module Not Found Error
```bash
pip install -r requirements.txt --upgrade
```

### cx_Oracle Installation Issues (Windows)
1. Download Oracle Instant Client
2. Extract to C:\oracle\instantclient_XX_X
3. Add to PATH environment variable
4. Reinstall cx_Oracle: `pip install cx_oracle --upgrade`

## Default Credentials (If you seed the database)

You can create an initial admin user:

```python
python
>>> from app import app, db
>>> from models import User
>>> with app.app_context():
...     admin = User(name="Admin", username="admin", email="admin@example.com", role="admin")
...     admin.set_password("admin123")
...     db.session.add(admin)
...     db.session.commit()
>>> exit()
```

## Next Steps

- Read the full README.md for detailed documentation
- Customize templates in `templates/` folder
- Modify styles in `static/css/style.css`
- Add new features by creating routes in `routes/`

## Support

For detailed documentation, see README.md
For issues, check the troubleshooting section

---

Happy Blogging! 🚀

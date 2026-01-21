@echo off
REM Flask Blog Application Deployment Script for Windows

echo Starting Flask Blog Application deployment...

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Python is not installed
    exit /b 1
)

REM Create virtual environment if it doesn't exist
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
echo Installing dependencies...
pip install -r requirements.txt

REM Create .env file if it doesn't exist
if not exist ".env" (
    echo Creating .env file from template...
    copy .env.example .env
    echo Please update .env file with your configuration
)

REM Initialize database
echo Initializing database...
flask db init 2>nul || echo Database already initialized
flask db migrate -m "Initial migration" 2>nul || echo No new migrations
flask db upgrade

echo Deployment complete!
echo Run 'python app.py' to start the application
pause

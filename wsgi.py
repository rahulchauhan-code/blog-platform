"""WSGI entry point for production servers like Gunicorn on Render"""
from app import app

if __name__ == "__main__":
    app.run()
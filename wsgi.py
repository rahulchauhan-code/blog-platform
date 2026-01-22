from app import app

# Expose the WSGI `app` callable for Gunicorn/Render.
# Keep the module import side-effects (app creation) minimal.
if __name__ == "__main__":
    # Local run for debugging; in production Gunicorn will import this module.
    app.run(host='0.0.0.0', port=int(__import__('os').environ.get('PORT', 5000)))
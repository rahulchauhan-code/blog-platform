# Multi-Language Blogging Platform - Flask Edition

A feature-rich blogging platform built with Flask that supports multi-language translation using the MyMemory API. Users can write posts in their native language and readers can view content in their preferred language.

## Features

- 🔐 User authentication (Register, Login, Logout)
- 📝 Create, Read, Update, Delete (CRUD) operations for blog posts
- 🌍 Multi-language support with real-time translation (12+ languages)
- 👤 User profiles with bio
- 📱 Responsive design for mobile and desktop
- 🔍 Category-based post organization
- ✨ Clean and modern UI
- 🔒 Secure password hashing

## Technology Stack

- **Backend:** Python Flask
- **Database:** PostgreSQL (Render)
- **ORM:** SQLAlchemy
- **Authentication:** Flask-Login
- **Translation:** MyMemory API
- **Frontend:** HTML5, CSS3, JavaScript (Jinja2 Templates)
- **Migration:** Flask-Migrate

## Project Structure

```
flask-blog-app/
├── app.py                  # Main application entry point
├── config.py              # Configuration settings
├── models.py              # Database models
├── requirements.txt       # Python dependencies
├── routes/               # Application routes (blueprints)
│   ├── __init__.py
│   ├── main.py          # Main routes
│   ├── auth.py          # Authentication routes
│   └── posts.py         # Post management routes
├── services/            # Business logic services
│   ├── __init__.py
│   └── translation_service.py
├── templates/           # Jinja2 HTML templates
│   ├── base.html
│   ├── index.html
│   ├── about.html
│   ├── profile.html
│   ├── auth/
│   │   ├── login.html
│   │   └── register.html
│   ├── posts/
│   │   ├── create.html
│   │   ├── view.html
│   │   ├── edit.html
│   │   └── my_posts.html
│   └── errors/
│       ├── 404.html
│       └── 500.html
└── static/              # Static files
    ├── css/
    │   └── style.css
    └── js/
        └── main.js
```

## Installation & Setup

### Prerequisites

- Python 3.8 or higher
- PostgreSQL (Render)
- pip (Python package manager)

### Step 1: Clone or Navigate to the Project

```bash
cd "d:\F-Project\Multi language Blogging Platform\flask-blog-app"
```

### Step 2: Create Virtual Environment

```bash
python -m venv venv
```

### Step 3: Activate Virtual Environment

**Windows:**
```bash
venv\Scripts\activate
```

**Linux/Mac:**
```bash
source venv/bin/activate
```

### Step 4: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 5: Configure Environment Variables

Copy the example environment file and update with your settings:

```bash
copy .env.example .env
```

Edit `.env` with your values:

```
FLASK_ENV=development
SECRET_KEY=your-secret-key-here
DATABASE_URL=postgresql://username:password@host:5432/dbname
TRANSLATION_API_URL=https://api.mymemory.translated.net/get
TRANSLATION_ENABLED=true
```

### Step 6: Initialize Database

```bash
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

Or create tables directly (for development):

```python
python
>>> from app import app, db
>>> with app.app_context():
>>>     db.create_all()
>>> exit()
```

### Step 7: Run the Application

```bash
python app.py
```

Or using Flask CLI:

```bash
flask run
```

The application will be available at `http://localhost:5000`

## Deploy to Render (Production)

**Start Command:**

```
gunicorn wsgi:app
```

**Environment Variables to set in Render:**

- `DATABASE_URL` (Render provides this automatically when you attach a PostgreSQL database)
- `SECRET_KEY` (required)
- `FLASK_ENV=production`
- `TRANSLATION_ENABLED=false` (recommended for production to avoid rate limits)
- `TRANSLATION_API_URL=https://api.mymemory.translated.net/get` (optional override)
- `TRANSLATION_API_KEY` (optional)
- `DEBUG_KEY` (optional, to protect `/_debug_db` endpoint)

**Notes:**
- Render sets `PORT` automatically; no manual setting needed.

## Database Configuration

### Using PostgreSQL (Render)

Set `DATABASE_URL` in your Render service environment variables. Render provides this value automatically when you attach a PostgreSQL database.

### Using SQLite (For Development)

Edit `config.py` and change the database URI:

```python
SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
```

Then install SQLite support:
```bash
pip install flask-sqlalchemy
```

### Using PostgreSQL

```python
SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
```

```bash
pip install psycopg2-binary
```

### Using MySQL

```python
SQLALCHEMY_DATABASE_URI = 'mysql://username:password@localhost/dbname'
```

```bash
pip install pymysql
```

## Usage

### User Registration

1. Navigate to `/auth/register`
2. Fill in your details (name, username, email, password)
3. Click "Register"

### Login

1. Navigate to `/auth/login`
2. Enter your email and password
3. Optionally check "Remember me"
4. Click "Login"

### Creating a Post

1. After logging in, click "Create Post" in the navigation
2. Enter post title, content, and category
3. Choose status (Draft or Published)
4. Click "Create Post"

### Translating Content

1. Use the language selector in the navigation bar
2. Select your preferred language
3. The page will reload with translated content

## API Endpoints

### Authentication Routes (`/auth`)
- `GET/POST /auth/login` - User login
- `GET/POST /auth/register` - User registration
- `GET /auth/logout` - User logout

### Post Routes (`/posts`)
- `GET /posts/` - List all posts
- `GET/POST /posts/create` - Create new post
- `GET /posts/<id>` - View single post
- `GET/POST /posts/<id>/edit` - Edit post
- `POST /posts/<id>/delete` - Delete post
- `GET /posts/my-posts` - View user's posts

### Main Routes
- `GET /` - Home page
- `GET /about` - About page
- `GET /profile/<user_id>` - User profile

## Supported Languages

- English (en)
- Spanish (es)
- French (fr)
- German (de)
- Italian (it)
- Portuguese (pt)
- Russian (ru)
- Japanese (ja)
- Korean (ko)
- Chinese (zh)
- Arabic (ar)
- Hindi (hi)

## Troubleshooting

### Database Connection Issues

If you encounter database connection errors:

1. Verify the Render PostgreSQL database is running
2. Check the `DATABASE_URL` value in Render
3. Ensure the host is reachable from your app environment
4. Test connection using `psql` or a DB client

### Translation API Issues

If translations aren't working:

1. Check internet connection
2. Check API logs in console

### Import Errors

If you get module import errors:

```bash
pip install -r requirements.txt --upgrade
```

## Development

### Adding New Routes

1. Create a new blueprint in `routes/`
2. Define your routes
3. Register blueprint in `app.py`

### Adding New Models

1. Define model in `models.py`
2. Run migrations:
```bash
flask db migrate -m "Add new model"
flask db upgrade
```

### Customizing Styles

Edit `static/css/style.css` to customize the appearance.

## Security Considerations

- Change `SECRET_KEY` in production
- Avoid hardcoding sensitive data in shared repositories
- Enable HTTPS in production
- Implement CSRF protection (Flask-WTF)
- Use strong passwords
- Regular security updates

## Future Enhancements

- [ ] Rich text editor for posts
- [ ] Image upload functionality
- [ ] Comments system
- [ ] Like/favorite posts
- [ ] Search functionality
- [ ] RSS feed
- [ ] Email notifications
- [ ] Social media sharing
- [ ] Admin dashboard
- [ ] API endpoints (REST API)

## License

This project is open-source and available for educational purposes.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Support

For issues and questions, please create an issue in the repository.

## Credits

- Flask Framework
- MyMemory for translation services
- PostgreSQL (Render)
- SQLAlchemy ORM

---

**Developed with ❤️ using Python Flask**

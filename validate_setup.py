"""
Flask Blog Application - Setup Validator
This script checks if the project is properly set up
"""

import os
import sys

def check_file(path, name):
    """Check if a file exists"""
    if os.path.exists(path):
        print(f"✓ {name}")
        return True
    else:
        print(f"✗ {name} - MISSING")
        return False

def check_directory(path, name):
    """Check if a directory exists"""
    if os.path.isdir(path):
        print(f"✓ {name}/")
        return True
    else:
        print(f"✗ {name}/ - MISSING")
        return False

def validate_setup():
    """Validate the complete project setup"""
    print("=" * 60)
    print("Flask Blog Application - Setup Validation")
    print("=" * 60)
    
    errors = []
    
    print("\n📁 Checking Core Files...")
    core_files = [
        ('app.py', 'Main application'),
        ('config.py', 'Configuration'),
        ('models.py', 'Database models'),
        ('requirements.txt', 'Dependencies'),
        ('.env.example', 'Environment template'),
        ('.gitignore', 'Git ignore'),
    ]
    
    for file, desc in core_files:
        if not check_file(file, f"{desc} ({file})"):
            errors.append(file)
    
    print("\n📂 Checking Directories...")
    directories = [
        ('routes', 'Routes/Blueprints'),
        ('services', 'Services'),
        ('templates', 'Templates'),
        ('templates/auth', 'Auth templates'),
        ('templates/posts', 'Post templates'),
        ('templates/errors', 'Error templates'),
        ('static', 'Static files'),
        ('static/css', 'CSS files'),
        ('static/js', 'JavaScript files'),
    ]
    
    for dir, desc in directories:
        if not check_directory(dir, f"{desc} ({dir})"):
            errors.append(dir)
    
    print("\n🛣️ Checking Route Files...")
    route_files = [
        ('routes/__init__.py', 'Routes init'),
        ('routes/main.py', 'Main routes'),
        ('routes/auth.py', 'Auth routes'),
        ('routes/posts.py', 'Post routes'),
    ]
    
    for file, desc in route_files:
        if not check_file(file, f"{desc} ({file})"):
            errors.append(file)
    
    print("\n🔧 Checking Service Files...")
    service_files = [
        ('services/__init__.py', 'Services init'),
        ('services/translation_service.py', 'Translation service'),
    ]
    
    for file, desc in service_files:
        if not check_file(file, f"{desc} ({file})"):
            errors.append(file)
    
    print("\n🎨 Checking Template Files...")
    template_files = [
        ('templates/base.html', 'Base template'),
        ('templates/index.html', 'Home page'),
        ('templates/about.html', 'About page'),
        ('templates/profile.html', 'Profile page'),
        ('templates/auth/login.html', 'Login page'),
        ('templates/auth/register.html', 'Register page'),
        ('templates/posts/create.html', 'Create post'),
        ('templates/posts/edit.html', 'Edit post'),
        ('templates/posts/view.html', 'View post'),
        ('templates/posts/my_posts.html', 'My posts'),
        ('templates/errors/404.html', '404 error'),
        ('templates/errors/500.html', '500 error'),
    ]
    
    for file, desc in template_files:
        if not check_file(file, f"{desc} ({file})"):
            errors.append(file)
    
    print("\n💅 Checking Static Files...")
    static_files = [
        ('static/css/style.css', 'Main stylesheet'),
        ('static/js/main.js', 'Main JavaScript'),
    ]
    
    for file, desc in static_files:
        if not check_file(file, f"{desc} ({file})"):
            errors.append(file)
    
    print("\n📚 Checking Documentation...")
    doc_files = [
        ('README.md', 'Main documentation'),
        ('QUICKSTART.md', 'Quick start guide'),
        ('PROJECT_STRUCTURE.md', 'Structure docs'),
        ('MIGRATION_GUIDE.md', 'Migration guide'),
        ('CONVERSION_SUMMARY.md', 'Conversion summary'),
    ]
    
    for file, desc in doc_files:
        if not check_file(file, f"{desc} ({file})"):
            errors.append(file)
    
    print("\n🚀 Checking Deployment Scripts...")
    deploy_files = [
        ('deploy.sh', 'Linux/Mac deployment'),
        ('deploy.bat', 'Windows deployment'),
    ]
    
    for file, desc in deploy_files:
        if not check_file(file, f"{desc} ({file})"):
            errors.append(file)
    
    print("\n" + "=" * 60)
    
    if not errors:
        print("✅ ALL CHECKS PASSED!")
        print("=" * 60)
        print("\n🎉 Your Flask Blog Application is properly set up!")
        print("\nNext steps:")
        print("1. Copy .env.example to .env")
        print("2. Edit .env with your database credentials")
        print("3. Run: pip install -r requirements.txt")
        print("4. Run: flask db init && flask db migrate && flask db upgrade")
        print("5. Run: python app.py")
        print("\nAccess your app at: http://localhost:5000")
        return True
    else:
        print("❌ VALIDATION FAILED!")
        print("=" * 60)
        print(f"\n{len(errors)} file(s)/directory(ies) missing:")
        for error in errors:
            print(f"  - {error}")
        print("\nPlease ensure all files are created properly.")
        return False

def check_python_version():
    """Check Python version"""
    print("\n🐍 Checking Python Version...")
    version = sys.version_info
    if version.major == 3 and version.minor >= 8:
        print(f"✓ Python {version.major}.{version.minor}.{version.micro} (OK)")
        return True
    else:
        print(f"✗ Python {version.major}.{version.minor}.{version.micro} (Requires 3.8+)")
        return False

def check_environment():
    """Check if .env file exists"""
    print("\n🔧 Checking Environment Configuration...")
    if os.path.exists('.env'):
        print("✓ .env file exists")
        return True
    else:
        print("ℹ .env file not found (use .env.example as template)")
        return False

if __name__ == "__main__":
    print("\n" + "🔍" * 30)
    check_python_version()
    success = validate_setup()
    check_environment()
    print("\n" + "🔍" * 30 + "\n")
    
    if success:
        sys.exit(0)
    else:
        sys.exit(1)

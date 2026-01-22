from app import app
from models import User, Post, PostContent, db

def remove_test_data():
    with app.app_context():
        # Remove the test user inserted by create_test_data.py (username=testuser)
        user = User.query.filter_by(username='testuser').first()
        if not user:
            print('No test user found; nothing to remove.')
            return
        # Deleting the user will cascade to posts/post_content due to relationship cascade
        db.session.delete(user)
        db.session.commit()
        print('✅ Test user and related posts removed.')

if __name__ == '__main__':
    remove_test_data()

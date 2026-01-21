"""Create test data for the blog"""
from app import app, db
from models import User, Post, PostContent
from datetime import datetime

def create_test_data():
    with app.app_context():
        # Clear existing data
        db.session.query(PostContent).delete()
        db.session.query(Post).delete()
        db.session.query(User).delete()
        db.session.commit()
        
        # Create test user
        user = User(
            name='Test User',
            username='testuser',
            email='test@example.com',
            bio='A test user for the blog platform'
        )
        user.set_password('password123')
        db.session.add(user)
        db.session.flush()
        
        # Create test posts
        post1 = Post(
            author_id=user.user_id,
            category='Technology',
            status='published',
            created_at=datetime.utcnow()
        )
        db.session.add(post1)
        db.session.flush()
        
        # Create post content
        content1 = PostContent(
            postid=post1.post_id,
            title='Welcome to Our Blog',
            content='This is a test post to demonstrate the multi-language translation feature. The content should be translatable to multiple languages using the LibreTranslate API.'
        )
        db.session.add(content1)
        
        # Create another test post
        post2 = Post(
            author_id=user.user_id,
            category='Travel',
            status='published',
            created_at=datetime.utcnow()
        )
        db.session.add(post2)
        db.session.flush()
        
        content2 = PostContent(
            postid=post2.post_id,
            title='Exploring New Places',
            content='Travel opens up a whole new world of experiences. In this post, we share our favorite travel tips and destinations around the globe.'
        )
        db.session.add(content2)
        
        db.session.commit()
        print("✅ Test data created successfully!")
        print(f"   - Created user: {user.username}")
        print(f"   - Created 2 posts")

if __name__ == '__main__':
    create_test_data()

import os
# Force local SQLite for this test script to avoid attempting remote Postgres connection
os.environ.pop('DATABASE_URL', None)
os.environ.pop('SPRING_DATASOURCE_URL', None)

from app import app
from models import db, User, Post, PostContent
from datetime import datetime

with app.app_context():
    # Check if user exists
    user = User.query.filter_by(email='rahul123@gmail.com').first()
    if not user:
        user = User(name='Rahul Chauhan', username='rahul', email='rahul123@gmail.com', bio='Developer', role='user', create_at=datetime.utcnow())
        user.set_password('rahul123')
        db.session.add(user)
        db.session.commit()
        print('Created user Rahul Chauhan')
    else:
        print('User already exists')

    # Create 3 posts
    sample_posts = [
        {
            'title': 'Welcome to my blog',
            'content': 'This is the first test post. Hello world! This blog showcases multilingual support.',
            'category': 'Introduction',
            'status': 'published'
        },
        {
            'title': 'Travel Tips',
            'content': 'Some useful travel tips and tricks for frequent travelers.',
            'category': 'Travel',
            'status': 'published'
        },
        {
            'title': 'Flask + Translation',
            'content': 'How to integrate translation services in a Flask app.',
            'category': 'Tech',
            'status': 'published'
        }
    ]

    for sp in sample_posts:
        post = Post(author_id=user.user_id, category=sp['category'], status=sp['status'], created_at=datetime.utcnow())
        db.session.add(post)
        db.session.flush()
        pc = PostContent(postid=post.post_id, title=sp['title'], content=sp['content'])
        db.session.add(pc)
    
    db.session.commit()
    print('Added sample posts for Rahul Chauhan')

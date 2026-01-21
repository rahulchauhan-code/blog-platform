from app import app
from models import User, Post

with app.app_context():
    u = User.query.filter_by(email='rahul123@gmail.com').first()
    if not u:
        print('User not found')
    else:
        print('User:', u.name, 'id=', u.user_id)
        posts = Post.query.filter_by(author_id=u.user_id).all()
        print('Posts:', len(posts))
        for p in posts:
            print('-', p.post_id, p.category, p.status)

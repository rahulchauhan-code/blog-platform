from app import app
from models import Post

if __name__ == '__main__':
    with app.app_context():
        print('post_count=', Post.query.count())

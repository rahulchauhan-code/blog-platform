from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    user_id = db.Column('USER_ID', db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    bio = db.Column(db.Text)
    role = db.Column(db.String(20), default='user')
    create_at = db.Column('CREATEAT', db.DateTime, default=datetime.utcnow)
    
    # Relationship with posts
    posts = db.relationship('Post', backref='author', lazy=True, cascade='all, delete-orphan')
    
    def get_id(self):
        return str(self.user_id)
    
    def set_password(self, password):
        """Hash and set the password"""
        self.password = generate_password_hash(password)
    
    def check_password(self, password):
        """Check if the provided password matches the hash"""
        return check_password_hash(self.password, password)
    
    def __repr__(self):
        return f'<User {self.username}>'


class Post(db.Model):
    __tablename__ = 'post'
    
    post_id = db.Column('POSTID', db.Integer, primary_key=True)
    author_id = db.Column('AUTHORID', db.Integer, db.ForeignKey('users.USER_ID'), nullable=False)
    category = db.Column(db.String(100))
    status = db.Column(db.String(20), default='draft')  # draft, published
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship with post contents
    contents = db.relationship('PostContent', backref='post', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Post {self.post_id}>'


class PostContent(db.Model):
    __tablename__ = 'post_content'
    
    id = db.Column(db.Integer, primary_key=True)
    postid = db.Column(db.Integer, db.ForeignKey('post.POSTID'), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text, nullable=False)
    
    def __repr__(self):
        return f'<PostContent {self.id} - {self.title}>'

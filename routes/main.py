from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import current_user, login_required
from models import Post
from services import TranslationService

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """Home page with list of posts"""
    lang = request.args.get('lang', 'en')
    page = request.args.get('page', 1, type=int)
    per_page = 10
    
    # Get published posts with pagination
    pagination = Post.query.filter_by(status='published').order_by(
        Post.created_at.desc()
    ).paginate(page=page, per_page=per_page, error_out=False)
    
    posts = pagination.items
    
    # Translate posts if needed
    if lang and lang != 'en':
        for post in posts:
            if post.category:
                post.category = TranslationService.translate(post.category, source_lang='en', target_lang=lang)
            # Translate post title and content
            for content in post.contents:
                content.title = TranslationService.translate(content.title, source_lang='en', target_lang=lang)
                content.content = TranslationService.translate(content.content, source_lang='en', target_lang=lang)
    
    supported_languages = TranslationService.get_supported_languages()
    
    return render_template(
        'index.html',
        posts=posts,
        pagination=pagination,
        current_lang=lang,
        supported_languages=supported_languages
    )


@main_bp.route('/about')
def about():
    """About page""" 
    return render_template('about.html')


@main_bp.route('/profile/<int:user_id>')
def profile(user_id):
    """User profile page"""
    from models import User
    user = User.query.get_or_404(user_id)
    posts = Post.query.filter_by(author_id=user_id, status='published').order_by(
        Post.created_at.desc()
    ).all()
    return render_template('profile.html', user=user, posts=posts)

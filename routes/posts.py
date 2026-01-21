from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from models import db, Post, PostContent, User
from services import TranslationService
from datetime import datetime

posts_bp = Blueprint('posts', __name__)

@posts_bp.route('/')
def index():
    """List all published posts"""
    lang = request.args.get('lang', 'en')
    posts = Post.query.filter_by(status='published').order_by(Post.created_at.desc()).all()
    
    # Translate categories if lang parameter is provided
    if lang and lang != 'en':
        for post in posts:
            if post.category:
                post.category = TranslationService.translate_text(post.category, lang)
    
    return render_template('posts/index.html', posts=posts, current_lang=lang)


@posts_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    """Create a new post"""
    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')
        category = request.form.get('category')
        status = request.form.get('status', 'draft')
        
        # Create post
        post = Post(
            author_id=current_user.user_id,
            category=category,
            status=status,
            created_at=datetime.utcnow()
        )
        
        try:
            db.session.add(post)
            db.session.flush()  # Get the post_id
            
            # Create post content
            post_content = PostContent(
                postid=post.post_id,
                title=title,
                content=content
            )
            db.session.add(post_content)
            db.session.commit()
            
            flash('Post created successfully!', 'success')
            return redirect(url_for('posts.view', post_id=post.post_id))
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while creating the post.', 'danger')
            print(f"Error: {str(e)}")
    
    return render_template('posts/create.html')


@posts_bp.route('/<int:post_id>')
def view(post_id):
    """View a single post"""
    post = Post.query.get_or_404(post_id)
    lang = request.args.get('lang', 'en')
    
    # Translate content if lang parameter is provided
    if lang and lang != 'en':
        if post.category:
            post.category = TranslationService.translate_text(post.category, lang)
        
        for content in post.contents:
            content.title = TranslationService.translate_text(content.title, lang)
            content.content = TranslationService.translate_text(content.content, lang)
    
    return render_template('posts/view.html', post=post, current_lang=lang)


@posts_bp.route('/<int:post_id>/edit', methods=['GET', 'POST'])
@login_required
def edit(post_id):
    """Edit an existing post"""
    post = Post.query.get_or_404(post_id)
    
    # Check if user is the author
    if post.author_id != current_user.user_id:
        flash('You do not have permission to edit this post.', 'danger')
        return redirect(url_for('posts.view', post_id=post_id))
    
    if request.method == 'POST':
        category = request.form.get('category')
        status = request.form.get('status', 'draft')
        title = request.form.get('title')
        content = request.form.get('content')
        
        post.category = category
        post.status = status
        
        # Update first content or create new one
        if post.contents:
            post.contents[0].title = title
            post.contents[0].content = content
        else:
            post_content = PostContent(
                postid=post.post_id,
                title=title,
                content=content
            )
            db.session.add(post_content)
        
        try:
            db.session.commit()
            flash('Post updated successfully!', 'success')
            return redirect(url_for('posts.view', post_id=post_id))
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while updating the post.', 'danger')
            print(f"Error: {str(e)}")
    
    return render_template('posts/edit.html', post=post)


@posts_bp.route('/<int:post_id>/delete', methods=['POST'])
@login_required
def delete(post_id):
    """Delete a post"""
    post = Post.query.get_or_404(post_id)
    
    # Check if user is the author
    if post.author_id != current_user.user_id:
        flash('You do not have permission to delete this post.', 'danger')
        return redirect(url_for('posts.view', post_id=post_id))
    
    try:
        db.session.delete(post)
        db.session.commit()
        flash('Post deleted successfully!', 'success')
        return redirect(url_for('main.index'))
    except Exception as e:
        db.session.rollback()
        flash('An error occurred while deleting the post.', 'danger')
        print(f"Error: {str(e)}")
        return redirect(url_for('posts.view', post_id=post_id))


@posts_bp.route('/my-posts')
@login_required
def my_posts():
    """View current user's posts"""
    posts = Post.query.filter_by(author_id=current_user.user_id).order_by(Post.created_at.desc()).all()
    return render_template('posts/my_posts.html', posts=posts)

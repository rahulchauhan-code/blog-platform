from flask import Blueprint, render_template, request, redirect, url_for, flash, session, make_response, current_app
from flask_login import login_user, logout_user, current_user, login_required
from models import db, User
from datetime import datetime
import secrets
import logging

logger = logging.getLogger(__name__)
auth_bp = Blueprint('auth', __name__)


@auth_bp.before_app_request
def _redirect_authenticated_from_auth_pages():
    """If user is already authenticated (including via remember cookie),
    prevent access to login/register pages and redirect to home."""
    try:
        if current_user.is_authenticated:
            ep = request.endpoint or ''
            if ep.startswith('auth.') and ep in ('auth.login', 'auth.register'):
                return redirect(url_for('main.index'))
    except Exception:
        # If anything goes wrong, don't block the request flow
        pass

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """User login page"""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        # checkbox returns a string when checked; cast to bool
        remember = bool(request.form.get('remember'))
        
        user = User.query.filter_by(email=email).first()
        
        if user and user.check_password(password):
            login_user(user, remember=remember)
            # Make the session persistent if user asked to be remembered
            try:
                session.permanent = bool(remember)
            except Exception:
                pass
            flash('Logged in successfully!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page or url_for('main.index'))
        else:
            flash('Invalid email or password', 'danger')
    
    return render_template('auth/login.html')


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """User registration page"""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        name = request.form.get('name')
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        bio = request.form.get('bio', '')
        
        # Validation
        if password != confirm_password:
            flash('Passwords do not match', 'danger')
            return render_template('auth/register.html')
        
        # Check if user already exists
        if User.query.filter_by(email=email).first():
            flash('Email already registered', 'danger')
            return render_template('auth/register.html')
        
        if User.query.filter_by(username=username).first():
            flash('Username already taken', 'danger')
            return render_template('auth/register.html')
        
        # Create new user
        user = User(
            name=name,
            username=username,
            email=email,
            bio=bio,
            role='user',
            create_at=datetime.utcnow()
        )
        user.set_password(password)
        
        try:
            db.session.add(user)
            db.session.commit()
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('auth.login'))
        except Exception as e:
            db.session.rollback()
            flash('An error occurred during registration. Please try again.', 'danger')
            import logging
            logging.error(f"Error during registration: {str(e)}")
    
    return render_template('auth/register.html')


@auth_bp.route('/logout')
def logout():
    """User logout"""
    # Log out the user and clear persistent session and remember cookies
    try:
        # unset permanent session
        session.permanent = False
    except Exception:
        pass

    logout_user()

    # Prepare redirect response and remove cookies (session + remember)
    response = make_response(redirect(url_for('main.index')))
    try:
        # Delete the session cookie
        response.delete_cookie(current_app.session_cookie_name)
    except Exception:
        pass
    try:
        remember_name = current_app.config.get('REMEMBER_COOKIE_NAME', 'remember_token')
        response.delete_cookie(remember_name)
    except Exception:
        pass

    flash('You have been logged out.', 'info')
    return response


@auth_bp.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    """Allow a logged-in user to change their password. This will invalidate cookies and require re-login."""
    if request.method == 'POST':
        current = request.form.get('current_password')
        new = request.form.get('new_password')
        confirm = request.form.get('confirm_password')

        if not current or not new or not confirm:
            flash('Please fill out all fields.', 'danger')
            return render_template('auth/change_password.html')

        if new != confirm:
            flash('New passwords do not match.', 'danger')
            return render_template('auth/change_password.html')

        user = current_user
        if not user.check_password(current):
            flash('Current password is incorrect.', 'danger')
            return render_template('auth/change_password.html')

        # Update password
        user.set_password(new)
        try:
            db.session.add(user)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            flash('Failed to update password. Please try again.', 'danger')
            return render_template('auth/change_password.html')

        # Invalidate cookies and log out the user so they must re-authenticate
        try:
            session.permanent = False
        except Exception:
            pass
        logout_user()
        response = make_response(redirect(url_for('auth.login')))
        try:
            response.delete_cookie(current_app.session_cookie_name)
        except Exception:
            pass
        try:
            remember_name = current_app.config.get('REMEMBER_COOKIE_NAME', 'remember_token')
            response.delete_cookie(remember_name)
        except Exception:
            pass

        flash('Password changed successfully. Please log in again.', 'success')
        return response

    return render_template('auth/change_password.html')


@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    """Request password reset link"""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        user = User.query.filter_by(email=email).first()
        
        if user:
            # Generate reset token (store in session for demo; in production use email with token)
            reset_token = secrets.token_urlsafe(32)
            session[f'reset_token_{user.id}'] = reset_token
            session.permanent = True
            
            flash('Password reset link sent to your email (check for reset link below).', 'info')
            logger.info(f'Password reset requested for user {user.id}')
            
            # In production, send email; for demo show reset link
            return render_template('auth/forgot_password.html', 
                                 reset_link=url_for('auth.reset_password', user_id=user.id, token=reset_token, _external=True),
                                 show_link=True)
        else:
            # Don't reveal if email exists (security best practice)
            flash('If an account exists with that email, a reset link has been sent.', 'info')
            return redirect(url_for('auth.login'))
    
    return render_template('auth/forgot_password.html')


@auth_bp.route('/reset-password/<int:user_id>/<token>', methods=['GET', 'POST'])
def reset_password(user_id, token):
    """Reset password with token"""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    user = User.query.get(user_id)
    if not user:
        flash('Invalid reset link.', 'danger')
        return redirect(url_for('auth.login'))
    
    # Verify token
    stored_token = session.get(f'reset_token_{user_id}')
    if not stored_token or stored_token != token:
        flash('Reset link expired or invalid.', 'danger')
        return redirect(url_for('auth.forgot_password'))
    
    if request.method == 'POST':
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        if not new_password or not confirm_password:
            flash('Please fill out all fields.', 'danger')
            return render_template('auth/reset_password.html', user_id=user_id, token=token)
        
        if new_password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return render_template('auth/reset_password.html', user_id=user_id, token=token)
        
        if len(new_password) < 6:
            flash('Password must be at least 6 characters.', 'danger')
            return render_template('auth/reset_password.html', user_id=user_id, token=token)
        
        # Update password
        user.set_password(new_password)
        try:
            db.session.add(user)
            db.session.commit()
            # Clear reset token
            session.pop(f'reset_token_{user_id}', None)
            flash('Password reset successfully. Please log in.', 'success')
            logger.info(f'Password reset completed for user {user_id}')
            return redirect(url_for('auth.login'))
        except Exception as e:
            db.session.rollback()
            flash('Failed to reset password. Please try again.', 'danger')
            logger.error(f'Error resetting password: {e}')
            return render_template('auth/reset_password.html', user_id=user_id, token=token)
    
    return render_template('auth/reset_password.html', user_id=user_id, token=token)

    return render_template('auth/change_password.html')

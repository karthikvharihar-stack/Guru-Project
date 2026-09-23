from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app.extensions import db
from app.models.user import User

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('seva.dashboard'))
        
    if request.method == 'POST':
        email = (request.form.get('email') or '').strip().lower()
        password = request.form.get('password') or ''
        remember = bool(request.form.get('remember'))
        
        # 1. Check regular Devotee User
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            if not user.is_active:
                flash('Your account has been deactivated. Please contact support.', 'warning')
                return redirect(url_for('auth.login'))
            login_user(user, remember=remember)
            flash(f'Logged in successfully. Welcome, {user.name}!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page or url_for('seva.dashboard'))
            
        # 2. Check AdminUser (in case admin logs in from this form)
        from app.models.user import AdminUser
        admin = AdminUser.query.filter_by(email=email).first()
        if admin and admin.check_password(password):
            login_user(admin, remember=remember)
            flash(f'Logged in successfully. Welcome, Administrator {admin.name}!', 'success')
            return redirect(url_for('admin.dashboard'))
            
        flash('Invalid email or password. Please check your credentials.', 'danger')
            
    return render_template('auth/login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('seva.dashboard'))
        
    if request.method == 'POST':
        name = (request.form.get('name') or '').strip()
        email = (request.form.get('email') or '').strip().lower()
        password = request.form.get('password') or ''
        confirm_password = request.form.get('confirm_password')
        language = request.form.get('language') or 'english'
        
        if not name or not email or not password:
            flash('Please fill in all required fields.', 'danger')
            return render_template('auth/register.html', name=name, email=email)
            
        if confirm_password is not None and confirm_password != '' and password != confirm_password:
            flash('Passwords do not match. Please re-enter your password.', 'danger')
            return render_template('auth/register.html', name=name, email=email)
            
        if len(password) < 6:
            flash('Password must be at least 6 characters long.', 'danger')
            return render_template('auth/register.html', name=name, email=email)
            
        if User.query.filter_by(email=email).first():
            flash('This email address is already registered. Please log in.', 'warning')
            return redirect(url_for('auth.login'))
            
        new_user = User(
            name=name, 
            email=email, 
            preferred_language=language,
            is_active=True
        )
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()
        
        flash('Registration successful. Please log in to your account.', 'success')
        return redirect(url_for('auth.login'))
        
    return render_template('auth/register.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.index'))

@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email')
        user = User.query.filter_by(email=email).first()
        if user:
            # Send reset email logic here
            flash('Password reset link sent to your email.', 'info')
        else:
            flash('Email not found.', 'danger')
        return redirect(url_for('auth.login'))
    return render_template('auth/forgot_password.html')

@auth_bp.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    # Verify token logic here
    if request.method == 'POST':
        password = request.form.get('password')
        # user.set_password(password)
        # db.session.commit()
        flash('Password reset successfully.', 'success')
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password.html')

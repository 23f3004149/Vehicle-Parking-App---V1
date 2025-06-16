from functools import wraps
from flask import redirect, url_for, flash
from flask_login import current_user

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash("Please login to access this page.", "warning")
            return redirect(url_for('auth.login'))
        if current_user.role != 'admin':
            flash("You are not authorized to access this page.", "danger")
            return redirect(url_for('user.dashboard'))  # Redirect to user dashboard
        return f(*args, **kwargs)
    return decorated_function

def user_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash("Please login to access this page.", "warning")
            return redirect(url_for('auth.login'))
        if current_user.role != 'user':
            flash("You are not authorized to access this page.", "danger")
            return redirect(url_for('admin.dashboard'))  # Redirect to admin dashboard
        return f(*args, **kwargs)
    return decorated_function

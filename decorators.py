from functools import wraps
from flask import redirect, url_for, flash
from flask_login import current_user

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.is_authenticated and current_user.role != 'admin':
            flash("You are not authorized to access this page.", "danger")
            return redirect(url_for('user.user_dashboard'))  # Redirect to user dashboard
        return f(*args, **kwargs)
    return decorated_function

def user_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.is_authenticated and current_user.role != 'user':
            flash("You are not authorized to access this page.", "danger")
            return redirect(url_for('admin.admin_dashboard'))  # Redirect to admin dashboard
        return f(*args, **kwargs)
    return decorated_function

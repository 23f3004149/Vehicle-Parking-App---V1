from flask import Blueprint, render_template,request,redirect,flash,url_for
from flask_login import login_required
from decorators import user_required

user_bp = Blueprint('user', __name__)

@user_bp.route('/user')
@login_required
@user_required
def dashboard():
    return render_template('user/dashboard.html')
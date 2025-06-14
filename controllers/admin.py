from flask import Blueprint, render_template,request,redirect,flash,url_for
from flask_login import login_required
from decorators import admin_required

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/admin')
@login_required
@admin_required
def dashboard():
    return render_template('admin/dashboard.html')
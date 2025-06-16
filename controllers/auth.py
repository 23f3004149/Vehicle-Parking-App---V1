from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_login import login_user, logout_user, login_required
from models import db, User,Admin
from flask_bcrypt import Bcrypt
from datetime import timedelta

bcrypt = Bcrypt()
auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        full_name = request.form.get('full_name')
        username = request.form.get('username')
        email = request.form.get('email')
        address = request.form.get('address')
        pin_code = request.form.get('pin_code')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        existing_username = User.query.filter_by(username=username).first()
        existing_email = User.query.filter_by(email=email).first()

        if existing_username:
            flash('Username already taken. Choose another.')
            return redirect(url_for('auth.register'))
        if existing_email:
            flash('Email already registered. Try logging in.')
            return redirect(url_for('auth.register'))
        if password != confirm_password:
            flash('Passwords do not match!')
            return redirect(url_for('auth.register'))


        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

        
        new_user = User(
            full_name=full_name,
            username=username,
            email=email,
            address=address,
            pin_code=pin_code,
            password_hash=hashed_password,
            role='user' 
        )
        db.session.add(new_user)
        db.session.commit()

        flash('User registered successfully! Please login.')
        return redirect(url_for('auth.login'))

    return render_template('register.html')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        remember = 'remember' in request.form

        user = User.query.filter_by(username=username).first()
        admin = Admin.query.filter_by(username=username).first()
        
        if user and bcrypt.check_password_hash(user.password_hash, password):
            login_user(user, remember=remember, duration=timedelta(days=30))
            session['user_info'] = {'id': user.id, 'role': 'user'}
            flash('Login successful!')
            return redirect(url_for('user.dashboard'))
        
        if admin and bcrypt.check_password_hash(admin.password_hash, password):
            login_user(admin, remember=remember, duration=timedelta(days=30))
            session['user_info'] = {'id': admin.id, 'role': 'admin'}
            flash('Admin login successful!')
            return redirect(url_for('admin.dashboard'))
        

        flash('Invalid username or password')

    return render_template('login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    session.clear()
    flash('Logged out successfully!')
    return redirect(url_for('auth.login'))

from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from .models import User, Client
from . import db, login_manager
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from .utils import owner_required

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.dashboard'))

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            flash('Logged in successfully.', 'success')
            return redirect(url_for('dashboard.dashboard'))
        flash('Invalid username or password.', 'danger')

    return render_template('login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.dashboard'))

    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')  # optional extra
        password = request.form.get('password')
        role = request.form.get('role', 'client')

        if User.query.filter_by(username=username).first():
            flash('Username already exists.', 'warning')
            return redirect(url_for('auth.register'))

        user = User(username=username, role=role)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        # If registering a client, optionally create a Client profile (if email provided)
        if role == 'client':
            if not Client.query.filter_by(email=username).first():
                c = Client(name=username, email=username)
                db.session.add(c)
                db.session.commit()

        flash('Registration successful. Please log in.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('register.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out.', 'info')
    return redirect(url_for('auth.login'))

# loader for flask-login
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@auth_bp.route('/admin/impersonate/<int:client_id>')
@login_required
@owner_required
def impersonate_client(client_id):
    session['impersonate_client_id'] = client_id
    flash('Now impersonating client view.', 'info')
    return redirect(url_for('portal.portal_dashboard'))


@auth_bp.route('/admin/stop_impersonate')
@login_required
@owner_required
def stop_impersonate():
    session.pop('impersonate_client_id', None)
    flash('Stopped impersonation.', 'info')
    return redirect(url_for('dashboard.dashboard'))

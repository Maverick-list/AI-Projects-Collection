from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required, current_user
from models import User, db

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    role = request.args.get('role', 'student')
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            login_user(user)
            if user.role == 'admin' or user.role == 'guru':
                return redirect(url_for('guru.dashboard'))
            else:
                return redirect(url_for('murid.dashboard'))
        
        flash('Invalid username or password')
    return render_template('login.html', role=role)

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('landing'))

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        nama = request.form.get('nama')
        email = request.form.get('email')
        nis = request.form.get('nis')
        kelas = request.form.get('kelas')
        parent_contact = request.form.get('parent_contact')

        # Check if user exists
        if User.query.filter_by(username=username).first():
            flash('Username sudah digunakan')
            return redirect(url_for('auth.register'))

        new_user = User(
            username=username,
            nama=nama,
            email=email,
            role='student',
            nis=nis,
            kelas=kelas,
            parent_contact=parent_contact
        )
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()

        login_user(new_user)
        return redirect(url_for('murid.dashboard'))

    return render_template('register.html')

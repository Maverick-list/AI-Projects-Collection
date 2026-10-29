from flask import Blueprint, render_template
from flask_login import login_required, current_user

murid_bp = Blueprint('murid', __name__)

@murid_bp.route('/dashboard')
@login_required
def dashboard():
    if current_user.role != 'student':
        return "Unauthorized", 403
    return render_template('murid/dashboard.html')

@murid_bp.route('/profile')
@login_required
def profile():
    return render_template('murid/profile.html')

@murid_bp.route('/ujian')
@login_required
def ujian():
    return render_template('murid/ujian.html')

@murid_bp.route('/chatbot')
@login_required
def chatbot():
    return render_template('murid/chatbot.html')

@murid_bp.route('/live-teaching')
@login_required
def live_teaching():
    return render_template('murid/live_teaching.html')

@murid_bp.route('/rapor')
@login_required
def rapor():
    return render_template('murid/rapor.html')

@murid_bp.route('/jadwal')
@login_required
def jadwal():
    return render_template('murid/jadwal.html')

@murid_bp.route('/materi')
@login_required
def materi():
    return render_template('murid/materi.html')

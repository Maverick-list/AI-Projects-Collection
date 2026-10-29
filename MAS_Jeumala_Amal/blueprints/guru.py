from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user

guru_bp = Blueprint('guru', __name__)

@guru_bp.route('/dashboard')
@login_required
def dashboard():
    if current_user.role not in ['admin', 'guru']:
        return "Unauthorized", 403
    return render_template('guru/dashboard.html')

@guru_bp.route('/rapor', methods=['GET', 'POST'])
@login_required
def rapor_list():
    from models import db, Grade, User
    
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'add':
            student_id = request.form.get('student_id')
            subject = request.form.get('subject')
            tugas = float(request.form.get('tugas', 0))
            uts = float(request.form.get('uts', 0))
            uas = float(request.form.get('uas', 0))
            term = request.form.get('term', 'Ganjil 2024')
            
            total = (tugas * 0.3) + (uts * 0.3) + (uas * 0.4)
            grade_letter = 'A' if total >= 85 else 'B' if total >= 70 else 'C' if total >= 60 else 'D'
            
            new_grade = Grade(
                student_id=student_id,
                subject=subject,
                tugas=tugas,
                uts=uts,
                uas=uas,
                total=total,
                grade_letter=grade_letter,
                term=term
            )
            db.session.add(new_grade)
            db.session.commit()
            flash('Nilai berhasil ditambahkan', 'success')
            
        elif action == 'edit':
            grade_id = request.form.get('grade_id')
            grade = Grade.query.get(grade_id)
            if grade:
                grade.student_id = request.form.get('student_id')
                grade.subject = request.form.get('subject')
                grade.tugas = float(request.form.get('tugas', 0))
                grade.uts = float(request.form.get('uts', 0))
                grade.uas = float(request.form.get('uas', 0))
                grade.term = request.form.get('term') # Update term as well
                
                grade.total = (grade.tugas * 0.3) + (grade.uts * 0.3) + (grade.uas * 0.4)
                grade.grade_letter = 'A' if grade.total >= 85 else 'B' if grade.total >= 70 else 'C' if grade.total >= 60 else 'D'
                
                db.session.commit()
                flash('Nilai berhasil diperbarui', 'success')

        elif action == 'delete':
            grade_id = request.form.get('grade_id')
            grade = Grade.query.get(grade_id)
            if grade:
                db.session.delete(grade)
                db.session.commit()
                flash('Nilai berhasil dihapus', 'success')
                
        return redirect(url_for('guru.rapor_list'))

    # Fetch data for GET request
    grades = Grade.query.join(User).add_columns(User.nama, User.kelas, Grade.id, Grade.subject, Grade.tugas, Grade.uts, Grade.uas, Grade.total, Grade.grade_letter, Grade.term, Grade.student_id).all()
    students = User.query.filter_by(role='student').all()
    
    return render_template('guru/rapor_list.html', grades=grades, students=students)

@guru_bp.route('/bank-soal', methods=['GET', 'POST'])
@login_required
def bank_soal():
    from models import db, QuestionBank
    import json
    
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'add':
            subject = request.form.get('subject')
            grade_level = request.form.get('grade_level')
            question_type = request.form.get('question_type')
            text = request.form.get('text')
            correct_answer = request.form.get('correct_answer')
            weight = int(request.form.get('weight', 1))
            
            options = None
            if question_type == 'PG':
                opts = [
                    request.form.get('opt_a'),
                    request.form.get('opt_b'),
                    request.form.get('opt_c'),
                    request.form.get('opt_d')
                ]
                options = json.dumps(opts)
                
            new_question = QuestionBank(
                teacher_id=current_user.id,
                subject=subject,
                grade_level=grade_level,
                question_type=question_type,
                text=text,
                options=options,
                correct_answer=correct_answer,
                weight=weight
            )
            db.session.add(new_question)
            db.session.commit()
            flash('Soal berhasil ditambahkan', 'success')
            
        elif action == 'edit':
            question_id = request.form.get('question_id')
            q = QuestionBank.query.get(question_id)
            if q:
                q.subject = request.form.get('subject')
                q.grade_level = request.form.get('grade_level')
                q.question_type = request.form.get('question_type')
                q.text = request.form.get('text')
                q.correct_answer = request.form.get('correct_answer')
                q.weight = int(request.form.get('weight', 1))
                
                if q.question_type == 'PG':
                    opts = [
                        request.form.get('opt_a'),
                        request.form.get('opt_b'),
                        request.form.get('opt_c'),
                        request.form.get('opt_d')
                    ]
                    q.options = json.dumps(opts)
                
                db.session.commit()
                flash('Soal berhasil diperbarui', 'success')

        elif action == 'delete':
            question_id = request.form.get('question_id')
            q = QuestionBank.query.get(question_id)
            if q:
                db.session.delete(q)
                db.session.commit()
                flash('Soal berhasil dihapus', 'success')
                
        return redirect(url_for('guru.bank_soal'))

    questions = QuestionBank.query.filter_by(teacher_id=current_user.id).order_by(QuestionBank.id.desc()).all()
    # Parse options JSON for display
    for q in questions:
        if q.options:
            q.parsed_options = json.loads(q.options)
        else:
            q.parsed_options = []
            
    return render_template('guru/bank_soal.html', questions=questions)

@guru_bp.route('/live-teaching')
@login_required
def live_teaching():
    return render_template('guru/live_teaching.html')

@guru_bp.route('/absensi', methods=['GET', 'POST'])
@login_required
def absensi():
    from models import db, Attendance, User, datetime
    
    if request.method == 'POST':
        student_id = request.form.get('student_id')
        status = request.form.get('status')
        date_str = request.form.get('date') # Format YYYY-MM-DD
        
        # Parse date or default to now
        if date_str:
            timestamp = datetime.datetime.strptime(date_str, '%Y-%m-%d')
        else:
            timestamp = datetime.datetime.now()
            
        new_attendance = Attendance(
            user_id=student_id,
            status=status,
            method='Manual',
            timestamp=timestamp
        )
        db.session.add(new_attendance)
        db.session.commit()
        flash('Absensi berhasil dicatat', 'success')
        return redirect(url_for('guru.absensi'))

    # Fetch recent attendance
    attendance_list = Attendance.query.join(User).add_columns(User.nama, User.kelas, Attendance.timestamp, Attendance.status, Attendance.method).order_by(Attendance.timestamp.desc()).limit(50).all()
    students = User.query.filter_by(role='student').all()
    
    return render_template('guru/absensi.html', attendance_list=attendance_list, students=students)

@guru_bp.route('/absensi/export')
@login_required
def absensi_export():
    from models import Attendance, User
    import csv
    from flask import make_response
    import io

    # Fetch all data or filter by args (optional)
    attendance_list = Attendance.query.join(User).add_columns(User.nama, User.kelas, Attendance.timestamp, Attendance.status, Attendance.method).order_by(Attendance.timestamp.desc()).all()
    
    si = io.StringIO()
    cw = csv.writer(si)
    cw.writerow(['Waktu', 'Nama Siswa', 'Kelas', 'Status', 'Metode'])
    
    for r in attendance_list:
        cw.writerow([
            r.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            r.nama,
            r.kelas,
            r.status,
            r.method
        ])
        
    output = make_response(si.getvalue())
    output.headers["Content-Disposition"] = "attachment; filename=rekap_absensi.csv"
    output.headers["Content-type"] = "text/csv"
    return output

@guru_bp.route('/data-murid')
@login_required
def data_murid():
    from models import User
    murid_list = User.query.filter_by(role='student').all()
    return render_template('guru/data_murid.html', murid_list=murid_list)

@guru_bp.route('/tugas')
@login_required
def tugas():
    return render_template('guru/tugas.html')

@guru_bp.route('/pesan')
@login_required
def pesan():
    return render_template('guru/pesan.html')

from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import datetime

db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), nullable=False) # 'admin', 'guru', 'student'
    nama = db.Column(db.String(100), nullable=False)
    kelas = db.Column(db.String(20), nullable=True)
    nis = db.Column(db.String(20), nullable=True) # For students
    email = db.Column(db.String(100), nullable=True)
    address = db.Column(db.Text, nullable=True)
    parent_contact = db.Column(db.String(20), nullable=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Notification(db.Model):
    __tablename__ = 'notifications'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    message = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(20), default='info') # info, warning, success
    is_read = db.Column(db.Boolean, default=False)
    timestamp = db.Column(db.DateTime, default=datetime.datetime.now)


class Grade(db.Model):
    __tablename__ = 'grades'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    subject = db.Column(db.String(50), nullable=False)
    tugas = db.Column(db.Float, default=0.0)
    uts = db.Column(db.Float, default=0.0)
    uas = db.Column(db.Float, default=0.0)
    total = db.Column(db.Float, default=0.0)
    grade_letter = db.Column(db.String(2), nullable=True)
    term = db.Column(db.String(20), nullable=False) # e.g., 'Ganjil 2024'

class Attendance(db.Model):
    __tablename__ = 'attendance'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.datetime.now)
    status = db.Column(db.String(20), nullable=False) # 'Hadir', 'Izin', 'Sakit', 'Alpa'
    method = db.Column(db.String(20), default='Manual') # 'Manual' or 'Sensor'

class QuestionBank(db.Model):
    __tablename__ = 'question_bank'
    id = db.Column(db.Integer, primary_key=True)
    teacher_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    subject = db.Column(db.String(50), nullable=False)
    grade_level = db.Column(db.String(10), nullable=False)
    question_type = db.Column(db.String(20), nullable=False) # 'PG', 'Essay'
    text = db.Column(db.Text, nullable=False)
    options = db.Column(db.Text, nullable=True) # JSON string for PG
    correct_answer = db.Column(db.Text, nullable=False)
    weight = db.Column(db.Integer, default=1)

class Exam(db.Model):
    __tablename__ = 'exams'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    subject = db.Column(db.String(50), nullable=False)
    class_name = db.Column(db.String(20), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)
    duration_minutes = db.Column(db.Integer, nullable=False)
    # List of question IDs as a string for simplicity, or a separate association table
    questions_data = db.Column(db.Text, nullable=False) 

class ExamLog(db.Model):
    __tablename__ = 'exam_logs'
    id = db.Column(db.Integer, primary_key=True)
    exam_id = db.Column(db.Integer, db.ForeignKey('exams.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    event_type = db.Column(db.String(50), nullable=False) # 'tab_switch', 'face_not_focused', 'left_window'
    timestamp = db.Column(db.DateTime, default=datetime.datetime.now)

class Material(db.Model):
    __tablename__ = 'materials'
    id = db.Column(db.Integer, primary_key=True)
    class_name = db.Column(db.String(20), nullable=False)
    subject = db.Column(db.String(50), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    file_url = db.Column(db.String(200), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.datetime.now)

class Assignment(db.Model):
    __tablename__ = 'assignments'
    id = db.Column(db.Integer, primary_key=True)
    class_name = db.Column(db.String(20), nullable=False)
    subject = db.Column(db.String(50), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    deadline = db.Column(db.DateTime, nullable=False)
    file_url = db.Column(db.String(200), nullable=True)

class Submission(db.Model):
    __tablename__ = 'submissions'
    id = db.Column(db.Integer, primary_key=True)
    assignment_id = db.Column(db.Integer, db.ForeignKey('assignments.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    file_url = db.Column(db.String(200), nullable=False)
    submitted_at = db.Column(db.DateTime, default=datetime.datetime.now)
    grade = db.Column(db.Float, nullable=True)
    comment = db.Column(db.Text, nullable=True)

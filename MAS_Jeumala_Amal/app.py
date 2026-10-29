from flask import Flask, render_template
from flask_login import LoginManager
from models import db, User
import os
from dotenv import load_dotenv

load_dotenv()

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'mas-jeumala-amal-secret'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///madrasah.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Register Blueprints
    from blueprints.auth import auth_bp
    from blueprints.guru import guru_bp
    from blueprints.murid import murid_bp
    from blueprints.api import api_bp
    from blueprints.api_extra import api_extra_bp

    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(guru_bp, url_prefix='/guru')
    app.register_blueprint(murid_bp, url_prefix='/murid')
    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(api_extra_bp, url_prefix='/api/extra')

    @app.route('/')
    def landing():
        return render_template('landing.html')

    # Optimized DB Init: Only call create_all if database doesn't exist
    db_path = os.path.join(app.instance_path, 'madrasah.db')
    if not os.path.exists(db_path):
        print("DEBUG: Database not found. Initializing and seeding...")
        with app.app_context():
            db.create_all()
            # Seed admin
            admin = User.query.filter_by(username='admin').first()
            if not admin:
                admin = User(username='admin', role='admin', nama='Administrator', email='admin@jeumala.sch.id')
                admin.set_password('admin123')
                db.session.add(admin)
                
                # Seed a dummy teacher
                teacher = User(username='guru1', role='guru', nama='Ust. Ahmad', email='ahmad@jeumala.sch.id')
                teacher.set_password('guru123')
                db.session.add(teacher)

                # Seed a dummy student
                student = User(username='murid1', role='student', nama='Zaki', nis='12345', kelas='X IPA 1', email='zaki@jeumala.sch.id')
                student.set_password('murid123')
                db.session.add(student)

                db.session.commit()
                print("DEBUG: Database seeded successfully.")
    else:
        print("DEBUG: Database already exists. Skipping initialization.")

    return app

if __name__ == '__main__':
    app = create_app()
    # Threaded=True allows handling multiple requests even with long-running tasks
    app.run(debug=True, port=7777, threaded=True)

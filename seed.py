from app import app, db, bcrypt
from models import Admin

def seed_admin():
    with app.app_context():
        existing_admin = Admin.query.filter_by(username='admin').first()
        if existing_admin:
            print("Admin already exists.")
            return

        hashed_password = bcrypt.generate_password_hash('admin123').decode('utf-8')
        admin = Admin(username='admin', password_hash=hashed_password)
        db.session.add(admin)
        db.session.commit()
        print("Default admin created (username: admin, password: admin123)")

if __name__ == '__main__':
    seed_admin()

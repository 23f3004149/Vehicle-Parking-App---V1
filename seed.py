from app import app, db, bcrypt
from models import Admin, City

def seed_admin():
    existing_admin = Admin.query.filter_by(username='admin').first()
    if existing_admin:
        print("✅ Admin already exists.")
    else:
        hashed_password = bcrypt.generate_password_hash('admin123').decode('utf-8')
        admin = Admin(username='admin', password_hash=hashed_password)
        db.session.add(admin)
        print("✅ Default admin created (username: admin, password: admin123)")

def seed_cities():
    major_cities = [
        ("Varanasi", "Uttar Pradesh"),
        ("Lucknow", "Uttar Pradesh"),
        ("Delhi", "Delhi"),
        ("Mumbai", "Maharashtra"),
        ("Chennai", "Tamil Nadu"),
        ("Bengaluru", "Karnataka"),
        ("Hyderabad", "Telangana"),
        ("Kolkata", "West Bengal"),
        ("Pune", "Maharashtra"),
        ("Jaipur", "Rajasthan")
    ]

    count = 0
    for name, state in major_cities:
        if not City.query.filter_by(name=name, state=state).first():
            db.session.add(City(name=name, state=state))
            count += 1

    if count > 0:
        print(f"✅ {count} cities seeded successfully.")
    else:
        print("✅ Cities already seeded.")

if __name__ == '__main__':
    with app.app_context():
        seed_admin()
        seed_cities()
        db.session.commit()

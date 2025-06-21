from app import app, db, bcrypt
from models import Admin, City, User, ParkingLot, ParkingSpot
from datetime import datetime

def seed_admin():
    if not Admin.query.filter_by(username='admin').first():
        hashed_password = bcrypt.generate_password_hash('admin123').decode('utf-8')
        admin = Admin(username='admin', password_hash=hashed_password)
        db.session.add(admin)
        print("✅ Default admin created (username: admin, password: admin123)")
    else:
        print("✅ Admin already exists.")

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
    print(f"✅ {count} new cities added." if count > 0 else "✅ Cities already seeded.")

def seed_users():
    sample_users = [
        ("johndoe", "John Doe", "john@example.com", "password123", "MG Road, Bengaluru", "560001"),
        ("janesmith", "Jane Smith", "jane@example.com", "secure456", "Connaught Place, Delhi", "110001"),
        ("rahulverma", "Rahul Verma", "rahul@example.com", "hello789", "Sadar Bazar, Lucknow", "226002")
    ]
    count = 0
    for username, full_name, email, pwd, address, pin in sample_users:
        if not User.query.filter_by(username=username).first():
            hashed_pwd = bcrypt.generate_password_hash(pwd).decode('utf-8')
            user = User(username=username, full_name=full_name, email=email, password_hash=hashed_pwd, address=address, pin_code=pin)
            db.session.add(user)
            count += 1
    print(f"✅ {count} sample users added." if count > 0 else "✅ Users already seeded.")

def seed_parking_lots_and_spots():
    city = City.query.filter_by(name='Bengaluru').first()
    if city:
        lots_data = [
            {
                'prime_location_name': 'MG Road',
                'address': 'Near Metro Station',
                'pin_code': '560001',
                'price_per_hour': 20,
                'max_spots': 5
            },
            {
                'prime_location_name': 'Indiranagar',
                'address': 'Opp. CMH Road',
                'pin_code': '560038',
                'price_per_hour': 25,
                'max_spots': 6
            },
            {
                'prime_location_name': 'Koramangala',
                'address': '5th Block, Near Forum Mall',
                'pin_code': '560095',
                'price_per_hour': 30,
                'max_spots': 8
            },
            {
                'prime_location_name': 'Whitefield',
                'address': 'Near ITPL Main Road',
                'pin_code': '560066',
                'price_per_hour': 18,
                'max_spots': 10
            },
            {
                'prime_location_name': 'Godowlia Multilevel Parking',
                'address': 'Near Godowlia Chowk',
                'pin_code': '221001',
                'price_per_hour': 50,
                'max_spots': 20
            },
            {
                'prime_location_name': 'Shivpur',
                'address': 'Near Shivpur Fatak',
                'pin_code': '221003',
                'price_per_hour': 10,
                'max_spots': 10
            }
        ]

        for lot_data in lots_data:
            if not ParkingLot.query.filter_by(prime_location_name=lot_data['prime_location_name']).first():
                lot = ParkingLot(
                    city_id=city.id,
                    prime_location_name=lot_data['prime_location_name'],
                    address=lot_data['address'],
                    pin_code=lot_data['pin_code'],
                    price_per_hour=lot_data['price_per_hour'],
                    max_spots=lot_data['max_spots']
                )
                db.session.add(lot)
                db.session.flush()
                for _ in range(lot.max_spots):
                    spot = ParkingSpot(lot_id=lot.id)
                    db.session.add(spot)
                print(f"✅ Created lot and spots for {lot.prime_location_name}, Bengaluru.")
            else:
                print(f"ℹ️ Lot already exists for {lot_data['prime_location_name']}, Bengaluru.")
        
        db.session.commit()
    else:
        print("❌ Bengaluru city not found. Please seed cities first.")


if __name__ == '__main__':
    with app.app_context():
        seed_admin()
        seed_cities()
        seed_users()
        seed_parking_lots_and_spots()
        db.session.commit()

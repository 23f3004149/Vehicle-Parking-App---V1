from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()


# User and Admin Models


class User(db.Model, UserMixin):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    address = db.Column(db.String(200))
    pin_code = db.Column(db.String(10))
    role = db.Column(db.String(20), nullable=False, default='user')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    reservations = db.relationship('Reservation', backref='user', lazy=True)

    def __repr__(self):
        return f"<User {self.username}>"


class Admin(db.Model, UserMixin):
    __tablename__ = 'admin'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='admin')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Admin {self.username}>"


# -------------------------------
# City & Lot Models
# -------------------------------

class City(db.Model):
    __tablename__ = 'city'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    state = db.Column(db.String(100), nullable=False)

    lots = db.relationship('ParkingLot', backref='city', cascade='all, delete-orphan', lazy=True)

    def __repr__(self):
        return f"<City {self.name}, {self.state}>"


class ParkingLot(db.Model):
    __tablename__ = 'parking_lot'

    id = db.Column(db.Integer, primary_key=True)
    city_id = db.Column(db.Integer, db.ForeignKey('city.id'), nullable=False)
    prime_location_name = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(200))
    pin_code = db.Column(db.String(10))
    price_per_hour = db.Column(db.Float, nullable=False)
    max_spots = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    spots = db.relationship('ParkingSpot', backref='lot', cascade='all, delete-orphan', lazy=True)

    def occupied_count(self):
        return sum(1 for spot in self.spots if spot.is_occupied)

    def available_spots(self):
        return sum(1 for spot in self.spots if spot.status == 'A')

    def __repr__(self):
        return f"<ParkingLot {self.prime_location_name} in CityID {self.city_id}>"


# -------------------------------
# Parking Spot and Reservation
# -------------------------------

class ParkingSpot(db.Model):
    __tablename__ = 'parking_spot'

    id = db.Column(db.Integer, primary_key=True)
    lot_id = db.Column(db.Integer, db.ForeignKey('parking_lot.id', ondelete='CASCADE'), nullable=False)
    status = db.Column(db.String(1), default='A')  # A = Available, O = Occupied
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    reservation = db.relationship('Reservation', backref='spot', uselist=False)

    @property
    def is_occupied(self):
        return self.status == 'O'
    
    @property
    def is_available(self):
        return self.status == 'A'


    def __repr__(self):
        return f"<Spot {self.id} - Lot {self.lot_id} - {self.status}>"


class Reservation(db.Model):
    __tablename__ = 'reservation'

    id = db.Column(db.Integer, primary_key=True)
    spot_id = db.Column(db.Integer, db.ForeignKey('parking_spot.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    vehicle_number = db.Column(db.String(20), nullable=False)
    parking_timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    leaving_timestamp = db.Column(db.DateTime)
    parking_cost = db.Column(db.Float)
    is_active = db.Column(db.Boolean, default=True)

    def __repr__(self):
        return f"<Reservation {self.id} - User {self.user_id} - Spot {self.spot_id}>"

    @property
    def total_hours(self):
        if self.leaving_timestamp and self.parking_timestamp:
            duration = self.leaving_timestamp - self.parking_timestamp
            return round(duration.total_seconds() / 3600, 2)
        return 0

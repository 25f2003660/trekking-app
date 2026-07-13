from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(12), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(12), nullable=False)
    email = db.Column(db.String(120), default='')
    phone = db.Column(db.String(20), default='')

    is_blacklisted = db.Column(db.Boolean, default=False)

    def set_password(self, raw_password):
        self.password = generate_password_hash(raw_password)

    def check_password(self, raw_password):
        return check_password_hash(self.password, raw_password)


class StaffProfile(db.Model):
    __tablename__ = 'staff_profile'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False)
    name = db.Column(db.String(100))
    status = db.Column(db.String(20), default='Pending')

    user = db.relationship('User', backref=db.backref('staff_profile', uselist=False))


class Trek(db.Model):
    __tablename__ = 'trek'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    difficulty = db.Column(db.String(20), default='Moderate')
    duration = db.Column(db.Integer, default=1) 
    slots = db.Column(db.Integer, default=10)
    status = db.Column(db.String(20), default='Pending')
    assigned_staff_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    start_date = db.Column(db.String(20))
    end_date = db.Column(db.String(20))

    assigned_staff = db.relationship('User', foreign_keys=[assigned_staff_id])


class Booking(db.Model):
    __tablename__ = 'booking'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    trek_id = db.Column(db.Integer, db.ForeignKey('trek.id'), nullable=False)
    booking_date = db.Column(db.String(20))
    status = db.Column(db.String(20), default='Booked')
    payment_id = db.Column(db.String(100), default='')

    user = db.relationship('User')
    trek = db.relationship('Trek')

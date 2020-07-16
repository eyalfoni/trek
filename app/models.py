import jwt
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from hashlib import md5
from app import db, login
from time import time
from flask import current_app


users_to_trips_association_table = db.Table('users_trips',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id')),
    db.Column('trip_id', db.Integer, db.ForeignKey('trips.id')),
)


class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), index=True, unique=True)
    first_name = db.Column(db.String(64))
    last_name = db.Column(db.String(64))
    password_hash = db.Column(db.String(128))

    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    trips = db.relationship(
        "Trip",
        secondary=users_to_trips_association_table,
        back_populates="travelers")

    def __repr__(self):
        return '<User {}>'.format(self.email)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(
            digest, size)

    def get_reset_password_token(self, expires_in=600):
        return jwt.encode(
            {'reset_password': self.id, 'exp': time() + expires_in},
            current_app.config['SECRET_KEY'], algorithm='HS256').decode('utf-8')

    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(token, current_app.config['SECRET_KEY'],
                            algorithms=['HS256'])['reset_password']
        except:
            return
        return User.query.get(id)


class Trip(db.Model):
    __tablename__ = 'trips'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(64))

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    travelers = db.relationship(
        "User",
        secondary=users_to_trips_association_table,
        back_populates="trips")


class Flight(db.Model):
    __tablename__ = 'flights'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(64))
    trip_id = db.Column(db.Integer, db.ForeignKey('trips.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    start_datetime = db.Column(db.DateTime)
    end_datetime = db.Column(db.DateTime)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Stay(db.Model):
    __tablename__ = 'stays'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    trip_id = db.Column(db.Integer, db.ForeignKey('trips.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Event(db.Model):
    __tablename__ = 'events'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    trip_id = db.Column(db.Integer, db.ForeignKey('trips.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    created_at = db.Column(db.DateTime, default=datetime.utcnow)


@login.user_loader
def load_user(id):
    return User.query.get(int(id))


# TODO - make one to many relationship on flight, stay, event with users

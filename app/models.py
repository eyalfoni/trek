import jwt
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from hashlib import md5
from app import db, login
from time import time
from flask import current_app
from sqlalchemy.dialects.postgresql import JSONB


users_to_trips_association_table = db.Table(
    'users_trips',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id')),
    db.Column('trip_id', db.Integer, db.ForeignKey('trips.id')),
)

users_to_flights_association_table = db.Table(
    'users_flights',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id')),
    db.Column('flight_id', db.Integer, db.ForeignKey('flights.id')),
)

users_to_stays_association_table = db.Table(
    'users_stays',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id')),
    db.Column('stay_id', db.Integer, db.ForeignKey('stays.id')),
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
        back_populates="travelers"
    )

    flights = db.relationship(
        "Flight",
        secondary=users_to_flights_association_table,
        back_populates="users"
    )

    stays = db.relationship(
        "Stay",
        secondary=users_to_stays_association_table,
        back_populates="users"
    )

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

    @property
    def full_name(self):
        return self.first_name + ' ' + self.last_name


class Trip(db.Model):
    __tablename__ = 'trips'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(64))

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    travelers = db.relationship(
        "User",
        secondary=users_to_trips_association_table,
        back_populates="trips"
    )


class Flight(db.Model):
    __tablename__ = 'flights'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(64))
    trip_id = db.Column(db.Integer, db.ForeignKey('trips.id'))
    start_datetime = db.Column(db.DateTime)
    end_datetime = db.Column(db.DateTime)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    users = db.relationship(
        "User",
        secondary=users_to_flights_association_table,
        back_populates="flights"
    )


class Stay(db.Model):
    __tablename__ = 'stays'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    trip_id = db.Column(db.Integer, db.ForeignKey('trips.id'))
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    location = db.Column(JSONB)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    users = db.relationship(
        "User",
        secondary=users_to_stays_association_table,
        back_populates="stays"
    )


class Event(db.Model):
    __tablename__ = 'events'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    trip_id = db.Column(db.Integer, db.ForeignKey('trips.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    start_datetime = db.Column(db.DateTime)
    end_datetime = db.Column(db.DateTime)
    event_type = db.Column(db.String(64))
    location = db.Column(JSONB)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class SupplyItem(db.Model):
    __tablename__ = 'supplies'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    trip_id = db.Column(db.Integer, db.ForeignKey('trips.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    cost = db.Column(db.Numeric(precision=10, scale=2))
    is_done = db.Column(db.Boolean, default=False)
    cost_estimate = db.Column(db.Numeric(precision=10, scale=2))
    notes = db.Column(db.Text())

    user = db.relationship('User')


class Post(db.Model):
    __tablename__ = 'posts'

    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text())
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    trip_id = db.Column(db.Integer, db.ForeignKey('trips.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    comments = db.relationship("Comment")
    user = db.relationship('User')


class Comment(db.Model):
    __tablename__ = 'post_comments'

    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text())
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    user = db.relationship('User')


@login.user_loader
def load_user(id):
    return User.query.get(int(id))
